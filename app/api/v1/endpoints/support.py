from __future__ import annotations

import uuid
import json

from fastapi import APIRouter, Depends, WebSocket, WebSocketDisconnect
from pydantic import BaseModel
from sqlalchemy import select

from app.api.v1.deps import get_current_user, get_db
from app.db.models.support import Message, Ticket
from app.db.session import SessionLocal

router = APIRouter()


class TicketCreate(BaseModel):
    subject: str


class TicketOut(BaseModel):
    id: str
    subject: str
    status: str


class MessageCreate(BaseModel):
    ticket_id: str
    body: str
    sender: str = "user"


class MessageOut(BaseModel):
    id: str
    ticket_id: str
    sender: str
    body: str


@router.get("/support/tickets", response_model=list[TicketOut])
async def list_tickets(db=Depends(get_db), _=Depends(get_current_user)):
    result = await db.execute(select(Ticket).order_by(Ticket.created_at.desc()))
    rows = result.scalars().all()
    return [TicketOut(id=str(t.id), subject=t.subject, status=t.status) for t in rows]


@router.post("/support/tickets", response_model=TicketOut)
async def create_ticket(payload: TicketCreate, db=Depends(get_db), _=Depends(get_current_user)):
    t = Ticket(subject=payload.subject, status="open")
    db.add(t)
    await db.commit()
    await db.refresh(t)
    return TicketOut(id=str(t.id), subject=t.subject, status=t.status)


@router.get("/support/messages", response_model=list[MessageOut])
async def list_messages(ticket_id: str, db=Depends(get_db), _=Depends(get_current_user)):
    ticket_uuid = uuid.UUID(ticket_id)
    result = await db.execute(select(Message).where(Message.ticket_id == ticket_uuid))
    rows = result.scalars().all()
    return [MessageOut(id=str(m.id), ticket_id=str(m.ticket_id), sender=m.sender, body=m.body) for m in rows]


@router.post("/support/messages", response_model=MessageOut)
async def create_message(payload: MessageCreate, db=Depends(get_db), _=Depends(get_current_user)):
    m = Message(ticket_id=uuid.UUID(payload.ticket_id), sender=payload.sender, body=payload.body)
    db.add(m)
    await db.commit()
    await db.refresh(m)
    return MessageOut(id=str(m.id), ticket_id=str(m.ticket_id), sender=m.sender, body=m.body)


@router.websocket("/support/ws/{ticket_id}")
async def websocket_support(ws: WebSocket, ticket_id: str):
    try:
        ticket_uuid = uuid.UUID(ticket_id)
    except ValueError:
        await ws.close(code=1008)
        return
    await ws.accept()
    try:
        while True:
            raw = await ws.receive_text()
            data = json.loads(raw)
            body = str(data.get("body", "")).strip()
            sender = str(data.get("sender", "user")).strip()[:64] or "user"
            if body:
                async with SessionLocal() as db:
                    msg = Message(ticket_id=ticket_uuid, sender=sender, body=body)
                    db.add(msg)
                    await db.commit()
                await ws.send_text(
                    json.dumps({"ok": True, "ticket_id": str(ticket_uuid), "sender": sender, "body": body})
                )
            else:
                await ws.send_text(json.dumps({"ok": False, "error": "empty body"}))
    except WebSocketDisconnect:
        return

