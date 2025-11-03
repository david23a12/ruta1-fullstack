from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, Integer, String, Boolean, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os

app = FastAPI(title="ToDo API SQL - Día 6")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://ruta1-fullstack.vercel.app", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# DB SETUP
DATABASE_URL = "sqlite:///./tasks.db"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class TaskDB(Base):
    __tablename__ = "tasks"
    id = Column(Integer, primary_key=True, index=True)
    text = Column(String, index=True)
    completed = Column(Boolean, default=False)

# CREAR TABLA SI NO EXISTE
Base.metadata.create_all(bind=engine)

class Task(BaseModel):
    id: int | None = None
    text: str
    completed: bool = False

@app.get("/")
def home():
    return {"message": "API ToDo SQL - Día 6"}

@app.get("/tasks")
def get_tasks():
    db = SessionLocal()
    tasks = db.query(TaskDB).all()
    db.close()
    return [{"id": t.id, "text": t.text, "completed": t.completed} for t in tasks]

@app.post("/tasks")
def add_task(task: Task):
    db = SessionLocal()
    db_task = TaskDB(text=task.text, completed=task.completed)
    db.add(db_task)
    db.commit()
    db.refresh(db_task)
    db.close()
    return {"id": db_task.id, "text": db_task.text, "completed": db_task.completed}

@app.put("/tasks/{task_id}")
def update_task(task_id: int, task: Task):
    db = SessionLocal()
    db_task = db.query(TaskDB).filter(TaskDB.id == task_id).first()
    if not db_task:
        db.close()
        raise HTTPException(404, "Tarea no encontrada")
    db_task.text = task.text
    db_task.completed = task.completed
    db.commit()
    db.close()
    return {"id": db_task.id, "text": db_task.text, "completed": db_task.completed}

@app.delete("/tasks/{task_id}")
def delete_task(task_id: int):
    db = SessionLocal()
    db_task = db.query(TaskDB).filter(TaskDB.id == task_id).first()
    if not db_task:
        db.close()
        raise HTTPException(404, "Tarea no encontrada")
    db.delete(db_task)
    db.commit()
    db.close()
    return {"success": True}