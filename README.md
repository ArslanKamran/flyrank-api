# FlyRank Task API — v3 (Docker + Postgres)

A CRUD API that manages a to-do list, backed by a **PostgreSQL** database running in **Docker**.
Built with Python and FastAPI. Start the entire stack — app and database — with one command.

This is the third storage swap in the same repo:
> Memory (A1) → SQLite file (A2) → Containerized Postgres (A3 — this one)

The API on top never changed. Only the storage engine underneath.

---

## One command to run everything

```bash
cp .env.example .env
docker compose up
```

That's it. Docker builds the app image, starts the Postgres database, seeds 3 example tasks, and your API is live at **http://localhost:8000**.

No manual database setup. No installing Postgres. Works the same on any machine.

---

## Environment variables

Copy `.env.example` to `.env` and fill in your values:

```bash
cp .env.example .env
```

| Variable       | What it does                              | Example                                        |
|----------------|-------------------------------------------|------------------------------------------------|
| `DATABASE_URL` | Full Postgres connection string           | `postgresql://postgres:dev@localhost:5432/tasks` |

> ⚠️ Never commit `.env` — it's git-ignored. Only `.env.example` goes to GitHub.

---

## Endpoints

| Method | Endpoint           | Description              | Success Code |
|--------|--------------------|--------------------------|--------------|
| GET    | `/`                | API info                 | 200          |
| GET    | `/health`          | Health check             | 200          |
| GET    | `/tasks`           | List all tasks           | 200          |
| POST   | `/tasks`           | Create a task            | 201          |
| GET    | `/tasks/{id}`      | Get one task             | 200          |
| PUT    | `/tasks/{id}`      | Update a task            | 200          |
| DELETE | `/tasks/{id}`      | Delete a task            | 204          |

### Status codes

| Code | Meaning       | When                          |
|------|---------------|-------------------------------|
| 200  | OK            | GET / PUT success             |
| 201  | Created       | POST success                  |
| 204  | No Content    | DELETE success                |
| 400  | Bad Request   | Missing or empty title        |
| 404  | Not Found     | Task ID does not exist        |

---

## Example curl output

```
$ curl -i -X POST http://localhost:8000/tasks \
    -H "Content-Type: application/json" \
    -d '{"title": "Walk the dog", "done": false}'

HTTP/1.1 201 Created
content-type: application/json

{"id":4,"title":"Walk the dog","done":false}
```

---

## Database screenshot

The `tasks` table as seen from `psql` inside the Docker container:

![tasks table in psql](psql-screenshot.png)

---

## How to run (step by step)

```bash
# 1. Clone the repo
git clone https://github.com/ArslanKamran/flyrank-api.git
cd flyrank-api

# 2. Copy the env template
cp .env.example .env

# 3. Start everything
docker compose up
```

The database is created automatically. Three example tasks are seeded on the first run only.

To stop:
```bash
docker compose down
```

Your data persists across restarts because of the Docker **volume** (`taskdata`). Only `docker compose down -v` would delete it.

---

## Architecture

```
┌──────────────────┐       ┌─────────────────────┐
│   FastAPI app    │──────▶│   PostgreSQL (db)    │
│   (api service)  │       │   (db service)       │
│   port 8000      │       │   port 5432          │
└──────────────────┘       └─────────────────────┘
         │                          │
         └──── Docker network ──────┘
                    │
              taskdata volume
           (data lives here on disk)
```

Inside Docker Compose, the app reaches the database at the hostname `db` (the service name), not `localhost`.

---

## Storage history

| Assignment | Where tasks live        | What runs it          |
|------------|-------------------------|-----------------------|
| A1         | A list in memory        | Your Python process   |
| A2         | `tasks.db` file         | SQLite on disk        |
| A3 (this)  | Rows in Postgres        | A Docker container    |