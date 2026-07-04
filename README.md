# OteroSupport

**EN**: Real-time Support & Notifications (FastAPI + WebSockets)  
**ES**: Soporte y notificaciones en tiempo real (FastAPI + WebSockets)

## Live demo / Demo online
- **Web**: https://realtime-support-fastapi.vercel.app
- **API docs**: https://realtime-support-fastapi-api.onrender.com/docs
- **API health**: https://realtime-support-fastapi-api.onrender.com/api/v1/health

## Stack
- FastAPI
- WebSockets
- PostgreSQL
- Docker
- AI (Groq)

## Local setup (Docker)

`ash
cp .env.example .env
docker compose up --build
`

## Credentials (demo)

**EN**: Default demo admin is seeded from ADMIN_EMAIL / ADMIN_PASSWORD.  
**ES**: El admin demo se crea desde ADMIN_EMAIL / ADMIN_PASSWORD.

## Deploy

**EN**:
- Backend: Render (Blueprint via ender.yaml)
- Frontend: Vercel (Root Directory: web)

**ES**:
- Backend: Render (Blueprint con ender.yaml)
- Frontend: Vercel (Root Directory: web)
