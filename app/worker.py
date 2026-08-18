from app.redis_client import redis_client
from app.database import SessionLocal
from app.models import Task


def execute_task(task):
    if task.type == "addition":
        a = task.payload["a"]
        b = task.payload["b"]

        return a + b

    raise ValueError(f"Unknown task type: {task.type}")


def worker():
    print("Worker started. Waiting for tasks...")

    while True:
        _, task_id = redis_client.blpop("task_queue")

        print(f"Received task {task_id}")

        db = SessionLocal()

        try:
            task = db.query(Task).filter(Task.id == int(task_id)).first()

            if task is None:
                print(f"Task {task_id} not found")
                continue

            task.status = "running"
            db.commit()

            print(f"Executing task {task.id}")

            result = execute_task(task)

            task.result = result
            task.status = "completed"

            db.commit()

            print(f"Task {task.id} completed: {result}")

        except Exception as e:
            db.rollback()

            if task is not None:
                task.status = "failed"
                task.error = str(e)
                db.commit()

            print(f"Task {task_id} failed: {e}")

        finally:
            db.close()


if __name__ == "__main__":
    worker()