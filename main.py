from fastapi import FastAPI, HTTPException

app = FastAPI()

tasks = [
    {"id": 1, "title": "Buy milk", "done": False},
    {"id": 2, "title": "Study Python", "done": True},
    {"id": 3, "title": "Sleep", "done": False}
]

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