from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session

from .database import engine, SessionLocal
from .models import Base, Task


app = FastAPI(title="TaskForge")


# Create tables
Base.metadata.create_all(bind=engine)


# Database dependency
def get_db():
    db = SessionLocal()

    try:
        yield db
    finally:
        db.close()


@app.get("/")
def root():
    return {
        "message": "TaskForge is Running!"
    }


@app.post("/tasks")
def create_task(
    task_type: str,
    payload: dict,
    db: Session = Depends(get_db)
):
    task = Task(
        type=task_type,
        payload=payload
    )

    db.add(task)
    db.commit()
    db.refresh(task)

    return {
        "id": task.id,
        "type": task.type,
        "payload": task.payload,
        "status": task.status
    }


@app.get("/tasks")
def get_tasks(db: Session = Depends(get_db)):
    tasks = db.query(Task).all()

    return [
        {
            "id": task.id,
            "type": task.type,
            "payload": task.payload,
            "status": task.status
        }
        for task in tasks
    ]


@app.get("/tasks/{task_id}")
def get_task(task_id: int, db: Session = Depends(get_db)):
    task = db.query(Task).filter(Task.id == task_id).first()

    if not task:
        return {
            "error": "Task not found"
        }

    return {
        "id": task.id,
        "type": task.type,
        "payload": task.payload,
        "status": task.status
    }


@app.delete("/tasks/{task_id}")
def delete_task(task_id: int, db: Session = Depends(get_db)):
    task = db.query(Task).filter(Task.id == task_id).first()

    if not task:
        return {"error": "Task not found"}

    db.delete(task)
    db.commit()

    return {"message": "Task deleted successfully"}

@app.put("/tasks/{task_id}")
def update_task(
    task_id: int,
    type: str,
    payload: dict,
    status: str,
    db: Session = Depends(get_db)
):
    task = db.query(Task).filter(Task.id == task_id).first()

    if not task:
        return {"error": "Task not found"}

    task.type = type
    task.payload = payload
    task.status = status

    db.commit()
    db.refresh(task)

    return {
        "id": task.id,
        "type": task.type,
        "payload": task.payload,
        "status": task.status
    }