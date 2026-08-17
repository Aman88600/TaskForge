from fastapi.testclient import TestClient

from app.main import app
from .get_all_tasks import get_all_tasks

client = TestClient(app)


def test_root():
    response = client.get("/")

    assert response.status_code == 200
    assert response.json() == {
        "message": "TaskForge is Running!"
    }

def test_get_tasks():
    response = client.get("/tasks")

    assert response.status_code == 200
    tasks = get_all_tasks()
    print(tasks)

    data = response.json()
    for i,task in zip(data,tasks):
        assert i["id"] == task.id
        assert i["type"] == task.type
        assert i["payload"] == task.payload
        assert i["status"] == task.status


def test_get_task():
    response = client.get("/tasks/3/")

    assert response.status_code == 200
    data = response.json()
    assert data["type"] == "multiplication"
    assert data["payload"]["a"] == 10
    assert data["payload"]["b"] == 20    

def test_create_task():
    response = client.post(
        "/tasks",
        params={
            "task_type": "multiplication"
        },
        json={
            "a": 10,
            "b": 20
        }
    )

    assert response.status_code == 200

    data = response.json()

    assert data["type"] == "multiplication"
    assert data["payload"]["a"] == 10
    assert data["payload"]["b"] == 20