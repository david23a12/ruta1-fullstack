from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import json
import os
from typing import List

app = FastAPI(title="ToDo API - David Día 4")

# CORS: Permitir React
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Cambiar a tu Vercel URL después
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class Task(BaseModel):
    id: int
    text: str
    completed: bool = False

TASKS_FILE = "tasks.json"

def load_tasks() -> List[Task]:
    if os.path.exists(TASKS_FILE):
        with open(TASKS_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            return [Task(**t) for t in data]
    return []

def save_tasks(tasks: List[Task]):
    with open(TASKS_FILE, "w", encoding="utf-8") as f:
        json.dump([t.dict() for t in tasks], f, indent=2)

@app.get("/")
def home():
    return {"message": "API ToDo Full Stack - Día 4"}

@app.get("/tasks")
def get_tasks():
    return load_tasks()

@app.post("/tasks")
def add_task(task: Task):
    tasks = load_tasks()
    tasks.append(task)
    save_tasks(tasks)
    return task

@app.put("/tasks/{task_id}")
def update_task(task_id: int, task: Task):
    tasks = load_tasks()
    for i, t in enumerate(tasks):
        if t.id == task_id:
            tasks[i] = task
            save_tasks(tasks)
            return task
    raise HTTPException(404, "Tarea no encontrada")

@app.delete("/tasks/{task_id}")
def delete_task(task_id: int):
    tasks = load_tasks()
    new_tasks = [t for t in tasks if t.id != task_id]
    if len(new_tasks) == len(tasks):
        raise HTTPException(404, "Tarea no encontrada")
    save_tasks(new_tasks)
    return {"success": True}