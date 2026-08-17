from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
import os
from app.models import Task

load_dotenv()

YOUR_PASSWORD = os.getenv("psql_password")
DATABASE_URL = f"postgresql+psycopg://postgres:{YOUR_PASSWORD}@localhost:5432/taskforge"

engine = create_engine(DATABASE_URL)

SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False
)

tasks_local = []
def get_all_tasks():
    db = SessionLocal()

    tasks = db.query(Task).all()

    for task in tasks:
        # print(task.id, task.type, task.payload, task.status)
        tasks_local.append(task)

    db.close()
    return tasks_local

if __name__ == "__main__":
    tasks = get_all_tasks()
    for i in tasks:
        print(i.id)
        print(i.type)
        print(i.payload)
        print(i.status)


