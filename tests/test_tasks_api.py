from datetime import datetime, timedelta, timezone

import pytest


def task_payload(future_due_date: str) -> dict[str, str]:
    return {
        "title": "Prepare FastAPI interview",
        "description": "Build a compact task management API",
        "due_date": future_due_date,
    }


@pytest.mark.asyncio
async def test_create_and_get_task(client, future_due_date: str) -> None:
    create_response = await client.post("/api/v1/tasks", json=task_payload(future_due_date))

    assert create_response.status_code == 201
    created = create_response.json()["data"]
    assert created["id"] == 1
    assert created["title"] == "Prepare FastAPI interview"
    assert created["status"] == "pending"

    get_response = await client.get(f"/api/v1/tasks/{created['id']}")

    assert get_response.status_code == 200
    assert get_response.json()["data"]["id"] == created["id"]


@pytest.mark.asyncio
async def test_list_tasks_supports_status_filter_and_pagination(client, future_due_date: str) -> None:
    await client.post("/api/v1/tasks", json=task_payload(future_due_date))
    second_response = await client.post(
        "/api/v1/tasks",
        json={
            "title": "Ship tests",
            "description": None,
            "due_date": future_due_date,
        },
    )
    await client.put(
        f"/api/v1/tasks/{second_response.json()['data']['id']}",
        json={"status": "completed"},
    )

    response = await client.get(
        "/api/v1/tasks",
        params={"status": "pending", "limit": 10, "offset": 0},
    )

    assert response.status_code == 200
    tasks = response.json()["data"]["items"]
    assert len(tasks) == 1
    assert tasks[0]["status"] == "pending"


@pytest.mark.asyncio
async def test_update_task_triggers_async_notification(client, future_due_date: str, caplog) -> None:
    caplog.set_level("INFO")
    create_response = await client.post("/api/v1/tasks", json=task_payload(future_due_date))
    task_id = create_response.json()["data"]["id"]

    response = await client.put(f"/api/v1/tasks/{task_id}", json={"status": "completed"})

    assert response.status_code == 200
    assert response.json()["data"]["status"] == "completed"
    assert f"Email sent for task {task_id}" in caplog.text
    assert "title=Prepare FastAPI interview" in caplog.text
    assert "description=Build a compact task management API" in caplog.text
    assert "due_date=" in caplog.text
    assert "completed_at=" in caplog.text


@pytest.mark.asyncio
async def test_invalid_due_date_returns_422(client) -> None:
    past_due_date = (datetime.now(timezone.utc) - timedelta(days=1)).isoformat()

    response = await client.post(
        "/api/v1/tasks",
        json={
            "title": "Invalid task",
            "description": "Past due dates should fail",
            "due_date": past_due_date,
        },
    )

    assert response.status_code == 422
    assert "due_date must be in the future" in response.text


@pytest.mark.asyncio
async def test_not_found_returns_404(client) -> None:
    response = await client.get("/api/v1/tasks/999")

    assert response.status_code == 404
    assert response.json()["detail"] == "任务不存在"


@pytest.mark.asyncio
async def test_delete_task(client, future_due_date: str) -> None:
    create_response = await client.post("/api/v1/tasks", json=task_payload(future_due_date))
    task_id = create_response.json()["data"]["id"]

    delete_response = await client.delete(f"/api/v1/tasks/{task_id}")
    get_response = await client.get(f"/api/v1/tasks/{task_id}")

    assert delete_response.status_code == 200
    assert get_response.status_code == 404


@pytest.mark.asyncio
async def test_api_key_required(client, future_due_date: str) -> None:
    response = await client.post(
        "/api/v1/tasks",
        json=task_payload(future_due_date),
        headers={"X-API-Key": "wrong-key"},
    )

    assert response.status_code == 401
