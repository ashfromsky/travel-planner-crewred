# Travel Planner API

A RESTful API for managing travel projects and places from the
[Art Institute of Chicago](https://www.artic.edu/) collection.

Built with **FastAPI**, **SQLModel**, **SQLite**, and **Granian**.

---

## Tech Stack

- **FastAPI** — web framework
- **SQLModel** — ORM (built on SQLAlchemy + Pydantic)
- **SQLite** — database (via aiosqlite)
- **Granian** — ASGI server
- **httpx** — async HTTP client for AIC API

---

## Getting Started

### Option 1 — Docker (recommended)

```bash
git clone https://github.com/ashfromsky/travel-planner-crewred
cd travel-planner

cp .env.example .env

docker compose up --build
```

API will be available at: http://localhost:8000

---

### Option 2 — Local with uv

**Requirements:** Python 3.12+, [uv](https://docs.astral.sh/uv/)

```bash
git clone https://github.com/ashfromsky/travel-planner-crewred
cd travel-planner

cp .env.example .env

uv sync
uv run main.py
```

API will be available at: http://localhost:8000

---

## Environment Variables

Copy `.env.example` to `.env` and adjust if needed:

```env
DATABASE_URL=sqlite+aiosqlite:///./db.sqlite3
AIC_BASE_URL=https://api.artic.edu/api/v1
HOST=0.0.0.0
PORT=8000
WORKERS=1
```

> **Note:** Keep `WORKERS=1` when using SQLite to avoid write conflicts.

---

## API Documentation

Interactive Swagger UI is available at:

```
http://localhost:8000/docs
```

ReDoc alternative:

```
http://localhost:8000/redoc
```

---

## Endpoints Overview

### Projects

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/v1/projects/` | Create a project (optionally with places) |
| `GET` | `/api/v1/projects/` | List all projects |
| `GET` | `/api/v1/projects/{id}` | Get a single project with places |
| `PATCH` | `/api/v1/projects/{id}` | Update project info |
| `DELETE` | `/api/v1/projects/{id}` | Delete a project |

### Places

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/v1/projects/{id}/places/` | Add a place to a project |
| `GET` | `/api/v1/projects/{id}/places/` | List all places in a project |
| `GET` | `/api/v1/projects/{id}/places/{place_id}` | Get a single place |
| `PATCH` | `/api/v1/projects/{id}/places/{place_id}` | Update notes or mark as visited |

---

## Example Requests

### Create a project with places

```bash
curl -X POST http://localhost:8000/api/v1/projects/ \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Chicago Art Trip",
    "description": "My first museum visit",
    "start_date": "2025-08-01",
    "places": [
      {"external_id": 27992},
      {"external_id": 129884}
    ]
  }'
```

### Add a place to existing project

```bash
curl -X POST http://localhost:8000/api/v1/projects/1/places/ \
  -H "Content-Type: application/json" \
  -d '{"external_id": 4}'
```

### Mark a place as visited

```bash
curl -X PATCH http://localhost:8000/api/v1/projects/1/places/1 \
  -H "Content-Type: application/json" \
  -d '{"is_visited": true}'
```

### Update notes on a place

```bash
curl -X PATCH http://localhost:8000/api/v1/projects/1/places/1 \
  -H "Content-Type: application/json" \
  -d '{"notes": "Amazing painting, must see in Gallery 10"}'
```

---

## Business Logic

- A project can have **1 to 10 places**
- A place is validated against the **AIC API** before being added
- The same place **cannot be added twice** to the same project
- A project **cannot be deleted** if any of its places are marked as visited
- When **all places** in a project are visited, the project is automatically marked as `completed`
- AIC API responses are **cached in memory** to reduce external requests

---

## Project Structure

```
├── main.py               # App factory + lifespan
├── config.py             # Settings via pydantic-settings
├── database.py           # Async engine + session
├── models/
│   └── models.py         # SQLModel table definitions
├── schemas/
│   ├── project.py        # Request/response schemas
│   └── place.py
├── repositories/
│   ├── project_repo.py   # DB operations
│   └── place_repo.py
├── services/
│   ├── project_service.py  # Business logic
│   ├── place_service.py
│   └── aic_service.py    # AIC API client + cache
└── routers/
    ├── projects.py       # HTTP layer
    └── places.py
```

---

## Valid AIC Artwork IDs for Testing

| ID | Title |
|----|-------|
| `27992` | A Sunday on La Grande Jatte |
| `129884` | Starry Night and the Astronauts |
| `4` | Nighthawks |
| `28560` | The Bedroom |
| `16487` | American Gothic |