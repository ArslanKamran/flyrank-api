import sqlite3
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI()


# ──────────────────────────────────────────────
# Stage 0 · Database setup
# ──────────────────────────────────────────────

def get_db():
    """Open a connection to tasks.db with row_factory so rows come back as dicts."""
    conn = sqlite3.connect("tasks.db")
    conn.row_factory = sqlite3.Row
    return conn


def setup_database():
    """
    Create the tasks table if it doesn't exist yet,
    then seed 3 example tasks — but ONLY if the table is empty.
    This makes sure the seed never duplicates on restart.
    """
    conn = get_db()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS tasks (
            id    INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT    NOT NULL,
            done  INTEGER NOT NULL DEFAULT 0
        )
    """)
    count = conn.execute("SELECT COUNT(*) FROM tasks").fetchone()[0]
    if count == 0:
        conn.executemany(
            "INSERT INTO tasks (title, done) VALUES (?, ?)",
            [
                ("Buy milk",     0),
                ("Study Python", 1),
                ("Sleep",        0),
            ],
        )
    conn.commit()
    conn.close()


# Run setup once when the server starts
setup_database()


# ──────────────────────────────────────────────
# Pydantic model (same as Assignment 1)
# ──────────────────────────────────────────────

class Task(BaseModel):
    title: str
    done: bool = False


# ──────────────────────────────────────────────
# Utility routes
# ──────────────────────────────────────────────

@app.get("/")
def read_root():
    return {"name": "Task API", "version": "2.0", "endpoints": ["/tasks"]}


@app.get("/health")
def health_check():
    return {"status": "ok"}


# ──────────────────────────────────────────────
# Stage 1 · Read from the database
# ──────────────────────────────────────────────

@app.get("/tasks")
def get_tasks():
    conn = get_db()
    rows = conn.execute("SELECT * FROM tasks").fetchall()
    conn.close()
    return [dict(row) for row in rows]


@app.get("/tasks/{task_id}")
def get_task(task_id: int):
    conn = get_db()
    row = conn.execute(
        "SELECT * FROM tasks WHERE id = ?", (task_id,)
    ).fetchone()
    conn.close()
    if not row:
        raise HTTPException(status_code=404, detail="Task not found")
    return dict(row)


# ──────────────────────────────────────────────
# Stage 2 · Create new tasks (INSERT)
# ──────────────────────────────────────────────

@app.post("/tasks", status_code=201)
def create_task(task: Task):
    if not task.title.strip():
        raise HTTPException(status_code=400, detail="Title missing")
    conn = get_db()
    cursor = conn.execute(
        "INSERT INTO tasks (title, done) VALUES (?, ?)",
        (task.title, int(task.done)),
    )
    conn.commit()
    new_id = cursor.lastrowid
    new_task = conn.execute(
        "SELECT * FROM tasks WHERE id = ?", (new_id,)
    ).fetchone()
    conn.close()
    return dict(new_task)


# ──────────────────────────────────────────────
# Stage 3 · Update and delete (UPDATE / DELETE)
# ──────────────────────────────────────────────

@app.put("/tasks/{task_id}")
def update_task(task_id: int, task: Task):
    if not task.title.strip():
        raise HTTPException(status_code=400, detail="Title missing")
    conn = get_db()
    existing = conn.execute(
        "SELECT * FROM tasks WHERE id = ?", (task_id,)
    ).fetchone()
    if not existing:
        conn.close()
        raise HTTPException(status_code=404, detail="Task not found")
    conn.execute(
        "UPDATE tasks SET title = ?, done = ? WHERE id = ?",
        (task.title, int(task.done), task_id),
    )
    conn.commit()
    updated = conn.execute(
        "SELECT * FROM tasks WHERE id = ?", (task_id,)
    ).fetchone()
    conn.close()
    return dict(updated)


@app.delete("/tasks/{task_id}", status_code=204)
def delete_task(task_id: int):
    conn = get_db()
    existing = conn.execute(
        "SELECT * FROM tasks WHERE id = ?", (task_id,)
    ).fetchone()
    if not existing:
        conn.close()
        raise HTTPException(status_code=404, detail="Task not found")
    conn.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
    conn.commit()
    conn.close()