from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI()

tasks = [
    {"id": 1, "title": "Buy milk", "done": False},
    {"id": 2, "title": "Study Python", "done": True},
    {"id": 3, "title": "Sleep", "done": False}
]

class Task(BaseModel):
    title: str
    done: bool = False

@app.get("/")
def read_root(): return {"name": "Task API", "version": "1.0", "endpoints": ["/tasks"]}

@app.get("/health")
def health_check(): return {"status": "ok"}

@app.get("/tasks")
def get_tasks(): return tasks

@app.get("/tasks/{task_id}")
def get_task(task_id: int):
    task = next((t for t in tasks if t["id"] == task_id), None)
    if not task: raise HTTPException(status_code=404, detail="Task not found")
    return task

@app.post("/tasks", status_code=201)
def create_task(task: Task):
    if not task.title.strip(): raise HTTPException(status_code=400, detail="Title missing")
    new_task = {"id": len(tasks) + 1, "title": task.title, "done": task.done}
    tasks.append(new_task)
    return new_task

@app.put("/tasks/{task_id}")
def update_task(task_id: int, task: Task):
    existing = next((t for t in tasks if t["id"] == task_id), None)
    if not existing: raise HTTPException(status_code=404, detail="Task not found")
    existing.update({"title": task.title, "done": task.done})
    return existing

@app.delete("/tasks/{task_id}", status_code=204)
def delete_task(task_id: int):
    global tasks
    if not any(t["id"] == task_id for t in tasks): raise HTTPException(status_code=404, detail="Task not found")
    tasks = [t for t in tasks if t["id"] != task_id]
    return