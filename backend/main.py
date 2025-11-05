from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, Integer, String, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from jose import JWTError, jwt
from passlib.context import CryptContext
from datetime import datetime, timedelta
import os

app = FastAPI(title="ToDo API JWT - Día 7")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://ruta1-fullstack.vercel.app", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# === JWT CONFIG ===
SECRET_KEY = "cambia_esta_clave_secreta_muy_larga_1234567890"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

# === DB SETUP ===
DATABASE_URL = "sqlite:///./tasks.db"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)  # SIN index=True NI autoincrement
    username = Column(String, unique=True)
    hashed_password = Column(String)

class TaskDB(Base):
    __tablename__ = "tasks"
    id = Column(Integer, primary_key=True)  # SIN index=True NI autoincrement
    text = Column(String)
    completed = Column(Boolean, default=False)
    user_id = Column(Integer)
Base.metadata.create_all(bind=engine)

# === MODELS ===
class UserIn(BaseModel):
    username: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str

class Task(BaseModel):
    id: int | None = None
    text: str
    completed: bool = False

# === HELPERS ===
def verify_password(plain, hashed):
    return pwd_context.verify(plain, hashed)

def get_password_hash(password):
    return pwd_context.hash(password)

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def get_current_user(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(status_code=401, detail="Invalid token")
        return username
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

def get_user_id(username: str):
    db = SessionLocal()
    user = db.query(User).filter(User.username == username).first()
    db.close()
    return user.id if user else None

# === ROUTES ===
@app.post("/register")
def register(user: UserIn):
    db = SessionLocal()
    db_user = db.query(User).filter(User.username == user.username).first()
    if db_user:
        db.close()
        raise HTTPException(400, "Usuario ya existe")
    hashed = get_password_hash(user.password)
    new_user = User(username=user.username, hashed_password=hashed)
    db.add(new_user)
    db.commit()
    # QUITA db.refresh(new_user) ← ESTO CAUSA EL 500 EN RENDER
    db.close()
    return {"message": "Usuario creado"}

@app.post("/login", response_model=Token)
def login(form: OAuth2PasswordRequestForm = Depends()):
    db = SessionLocal()
    user = db.query(User).filter(User.username == form.username).first()
    db.close()
    if not user or not verify_password(form.password, user.hashed_password):
        raise HTTPException(401, "Credenciales inválidas")
    token = create_access_token({"sub": user.username})
    return {"access_token": token, "token_type": "bearer"}

# === TAREAS PROTEGIDAS ===
@app.get("/tasks")
def get_tasks(current_user: str = Depends(get_current_user)):
    db = SessionLocal()
    user_id = get_user_id(current_user)
    tasks = db.query(TaskDB).filter(TaskDB.user_id == user_id).all()
    db.close()
    return [{"id": t.id, "text": t.text, "completed": t.completed} for t in tasks]

@app.post("/tasks")
def add_task(task: Task, current_user: str = Depends(get_current_user)):
    db = SessionLocal()
    user_id = get_user_id(current_user)
    db_task = TaskDB(text=task.text, completed=task.completed, user_id=user_id)
    db.add(db_task)
    db.commit()
    db.refresh(db_task)
    db.close()
    return {"id": db_task.id, "text": db_task.text, "completed": db_task.completed}

@app.put("/tasks/{task_id}")
def update_task(task_id: int, task: Task, current_user: str = Depends(get_current_user)):
    db = SessionLocal()
    user_id = get_user_id(current_user)
    db_task = db.query(TaskDB).filter(TaskDB.id == task_id, TaskDB.user_id == user_id).first()
    if not db_task:
        db.close()
        raise HTTPException(404, "Tarea no encontrada")
    db_task.text = task.text
    db_task.completed = task.completed
    db.commit()
    db.close()
    return {"id": db_task.id, "text": db_task.text, "completed": db_task.completed}

@app.delete("/tasks/{task_id}")
def delete_task(task_id: int, current_user: str = Depends(get_current_user)):
    db = SessionLocal()
    user_id = get_user_id(current_user)
    db_task = db.query(TaskDB).filter(TaskDB.id == task_id, TaskDB.user_id == user_id).first()
    if not db_task:
        db.close()
        raise HTTPException(404, "Tarea no encontrada")
    db.delete(db_task)
    db.commit()
    db.close()
    return {"success": True}