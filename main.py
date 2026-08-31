import os
import psycopg
from psycopg.rows import dict_row
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from dotenv import load_dotenv

# Load the DATABASE_URL from the .env file
load_dotenv()

app = FastAPI()

DATABASE_URL = os.environ["DATABASE_URL"]


# ──────────────────────────────────────────────
# Stage 1 · Database setup
# ──────────────────────────────────────────────

def get_db():
    """
    Open a connection to Postgres.
    row_factory=dict_row makes every row come back as a dict
    so we can return it directly from our endpoints.
    """
    return psycopg.connect(DATABASE_URL, row_factory=dict_row)


def setup_database():
    """
    Create the tasks table if it doesn't exist yet.
    Seed 3 example tasks — but ONLY if the table is empty.
    This means the seed never duplicates on restart.
    """
    conn = get_db()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS tasks (
            id    SERIAL  PRIMARY KEY,
            title TEXT    NOT NULL,
            done  BOOLEAN NOT NULL DEFAULT FALSE
        )
    """)
    count = conn.execute("SELECT COUNT(*) FROM tasks").fetchone()["count"]
    if count == 0:
        for title, done in [("Buy milk", False), ("Study Python", True), ("Sleep", False)]:
            conn.execute("INSERT INTO tasks (title, done) VALUES (%s, %s)", (title, done))
    conn.commit()
    conn.close()


# Run setup once when the server starts
setup_database()


# ──────────────────────────────────────────────
# Pydantic model (same shape as A1 and A2)
# ──────────────────────────────────────────────

class Task(BaseModel):
    title: str
    done: bool = False


# ──────────────────────────────────────────────
# Utility routes
# ──────────────────────────────────────────────

@app.get("/")
def read_root():
    return {"name": "Task API", "version": "3.0", "endpoints": ["/tasks"]}


@app.get("/health")
def health_check():
    return {"status": "ok"}


# ──────────────────────────────────────────────
# Stage 2 · Read from Postgres
# ──────────────────────────────────────────────

@app.get("/tasks")
def get_tasks():
    conn = get_db()
    rows = conn.execute("SELECT * FROM tasks").fetchall()
    conn.close()
    return rows


@app.get("/tasks/{task_id}")
def get_task(task_id: int):
    conn = get_db()
    row = conn.execute(
        "SELECT * FROM tasks WHERE id = %s", (task_id,)
    ).fetchone()
    conn.close()
    if not row:
        raise HTTPException(status_code=404, detail="Task not found")
    return row


# ──────────────────────────────────────────────
# Stage 3 · Create, update, delete on Postgres
# ──────────────────────────────────────────────

@app.post("/tasks", status_code=201)
def create_task(task: Task):
    if not task.title.strip():
        raise HTTPException(status_code=400, detail="Title missing")
    conn = get_db()
    row = conn.execute(
        "INSERT INTO tasks (title, done) VALUES (%s, %s) RETURNING *",
        (task.title, task.done),
    ).fetchone()
    conn.commit()
    conn.close()
    return row


@app.put("/tasks/{task_id}")
def update_task(task_id: int, task: Task):
    if not task.title.strip():
        raise HTTPException(status_code=400, detail="Title missing")
    conn = get_db()
    existing = conn.execute(
        "SELECT id FROM tasks WHERE id = %s", (task_id,)
    ).fetchone()
    if not existing:
        conn.close()
        raise HTTPException(status_code=404, detail="Task not found")
    row = conn.execute(
        "UPDATE tasks SET title = %s, done = %s WHERE id = %s RETURNING *",
        (task.title, task.done, task_id),
    ).fetchone()
    conn.commit()
    conn.close()
    return row


@app.delete("/tasks/{task_id}", status_code=204)
def delete_task(task_id: int):
    conn = get_db()
    existing = conn.execute(
        "SELECT id FROM tasks WHERE id = %s", (task_id,)
    ).fetchone()
    if not existing:
        conn.close()
        raise HTTPException(status_code=404, detail="Task not found")
    conn.execute("DELETE FROM tasks WHERE id = %s", (task_id,))
    conn.commit()
    conn.close()