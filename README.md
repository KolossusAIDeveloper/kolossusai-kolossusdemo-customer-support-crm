# Customer Support CRM

AI-powered Sales and Customer Support CRM built with React 18 + TypeScript + Vite (frontend) and FastAPI + PostgreSQL + Redis + Celery (backend).

## Features

- Lead capture and management with AI scoring
- Sales pipeline (Kanban board)
- Customer inbox with AI-suggested replies
- Task and follow-up tracking
- Workflow automation engine
- Analytics dashboards
- Role-based access control
- Audit logs
- Multi-tenant (organization-level data isolation)

## Quick Start

```bash
cp .env.example .env
# Edit .env with your values
docker-compose up --build
```

App runs at http://localhost

## Development

### Backend
```bash
cd backend
pip install -r requirements.txt
alembic upgrade head
uvicorn app.main:app --reload
```

### Frontend
```bash
cd frontend
npm install
npm run dev
```

## Tech Stack

- **Frontend**: React 18, TypeScript, Vite, Tailwind CSS, TanStack Query, Zustand
- **Backend**: FastAPI, SQLAlchemy, Alembic, Pydantic v2
- **Database**: PostgreSQL 15
- **Cache/Queue**: Redis 7, Celery
- **AI**: OpenAI / Anthropic (configurable via `AI_PROVIDER`)

## Environment Variables

See `.env.example` for all required variables.

## Tests

```bash
cd backend
pytest tests/
```
