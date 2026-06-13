# AtomQuest — Real-Time Video Support Platform

Browser-based real-time customer support platform with video calling, chat, recording, and admin operations.

## Tech Stack

| Layer | Technology |
|---|---|
| Frontend | React, Vite, Tailwind v4, Zustand, React Router, LiveKit Client |
| Backend | FastAPI, SQLAlchemy, Alembic, Celery, JWT |
| Database | PostgreSQL, Redis |
| Video/Audio | LiveKit OSS (Self-Hosted), WebRTC |
| Deployment | Docker, Docker Compose, Nginx |
| Monitoring | Prometheus, Grafana, Structlog |

## Quick Start

### Prerequisites

- Docker & Docker Compose
- Node.js 20+
- Python 3.12+

### Development (Docker)

```bash
# Copy environment file
cp .env.example .env

# Start all services
docker-compose up --build

# Access the app
# Frontend: http://localhost:80
# Backend API: http://localhost:8000/api/health
# LiveKit: ws://localhost:7880
```

### Development (Local)

**Frontend:**
```bash
cd frontend
npm install
npm run dev
```

**Backend:**
```bash
cd backend
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows
pip install -r requirements.txt
uvicorn app.main:app --reload
```

### Default Credentials

| Role | Email | Password |
|---|---|---|
| Admin | admin@atomquest.com | admin123 |
| Agent | agent@atomquest.com | agent123 |

## Project Structure

```
├── frontend/          # React + Vite
├── backend/           # FastAPI
├── nginx/             # Reverse proxy
├── prometheus/        # Metrics collection
├── grafana/           # Dashboards
├── docker-compose.yml
├── livekit.yaml       # LiveKit server config
└── .env.example
```

## API Documentation

Once running, visit: `http://localhost:8000/docs` (Swagger UI)
