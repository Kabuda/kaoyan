import os
from datetime import UTC, datetime, timedelta

os.environ["DATABASE_URL"] = "sqlite+pysqlite:///:memory:"
os.environ["JWT_SECRET"] = "test-secret-for-kaoyan-study-flow"
os.environ["INITIAL_ADMIN_USERNAME"] = "admin"
os.environ["INITIAL_ADMIN_PASSWORD"] = "change-me-now"
os.environ["UPLOAD_DIR"] = "test_uploads"

from fastapi.testclient import TestClient

from app.main import app


def auth_headers(client: TestClient) -> dict[str, str]:
    response = client.post(
        "/api/auth/login",
        json={"username": "admin", "password": "change-me-now"},
    )
    assert response.status_code == 200
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


def test_profile_defaults() -> None:
    with TestClient(app) as client:
        headers = auth_headers(client)
        response = client.get("/api/profile", headers=headers)

    assert response.status_code == 200
    body = response.json()
    assert body["first_english_score"] == 46
    assert body["target_math_score"] == 110
    assert body["target_408_score"] == 100
    assert body["target_total_score"] == 330


def test_task_template_and_state_changes() -> None:
    with TestClient(app) as client:
        headers = auth_headers(client)
        response = client.post(
            "/api/tasks/generate-daily-template",
            json={"plan_date": "2026-07-01"},
            headers=headers,
        )
        assert response.status_code == 200
        tasks = response.json()
        assert len(tasks) == 4

        task_id = tasks[0]["id"]
        complete_response = client.post(f"/api/tasks/{task_id}/complete", headers=headers)
        assert complete_response.status_code == 200
        assert complete_response.json()["status"] == "completed"

        list_response = client.get("/api/tasks?date=2026-07-01", headers=headers)

    assert list_response.status_code == 200
    assert len(list_response.json()) >= 4


def test_timer_finish_creates_study_record_and_blocks_second_timer() -> None:
    with TestClient(app) as client:
        headers = auth_headers(client)
        task_response = client.post(
            "/api/tasks",
            json={
                "plan_date": "2026-07-02",
                "subject": "math",
                "module": "advanced_math",
                "title": "高数极限专题",
                "task_type": "weakness",
                "estimated_minutes": 90,
                "priority": 1,
            },
            headers=headers,
        )
        assert task_response.status_code == 201
        task_id = task_response.json()["id"]

        start_response = client.post("/api/timer/start", json={"task_id": task_id}, headers=headers)
        assert start_response.status_code == 201

        conflict_response = client.post("/api/timer/start", json={"task_id": task_id}, headers=headers)
        assert conflict_response.status_code == 409

        finish_response = client.post(
            "/api/timer/finish",
            json={"summary": "完成基础题", "blockers": "计算速度慢", "quality": "medium"},
            headers=headers,
        )
        assert finish_response.status_code == 200

        records_response = client.get("/api/records?subject=math", headers=headers)

    assert records_response.status_code == 200
    records = records_response.json()
    assert any(record["title"] == "高数极限专题" for record in records)


def test_manual_record_and_dashboard_stats() -> None:
    now = datetime.now(UTC)
    with TestClient(app) as client:
        headers = auth_headers(client)
        record_response = client.post(
            "/api/records",
            json={
                "subject": "english",
                "module": "reading",
                "task_type": "weakness",
                "title": "英语阅读精读",
                "started_at": (now - timedelta(minutes=60)).isoformat(),
                "ended_at": now.isoformat(),
                "duration_minutes": 60,
                "summary": "阅读一篇",
                "quality": "high",
            },
            headers=headers,
        )
        assert record_response.status_code == 201

        stats_response = client.get("/api/stats/dashboard", headers=headers)
        range_response = client.get(
            f"/api/stats/range?start_date={now.date().isoformat()}&end_date={now.date().isoformat()}",
            headers=headers,
        )

    assert stats_response.status_code == 200
    stats = stats_response.json()
    assert stats["today_minutes"] >= 60
    assert len(stats["recent_7_days"]) == 7
    assert range_response.status_code == 200
    assert range_response.json()[0]["minutes"] >= 60


def test_weekly_review_crud() -> None:
    with TestClient(app) as client:
        headers = auth_headers(client)
        create_response = client.post(
            "/api/reviews/weekly",
            json={
                "week_start": "2026-07-06",
                "summary": "数学投入不错",
                "biggest_problem": "英语阅读慢",
                "next_week_adjustment": "英语每天一篇阅读",
            },
            headers=headers,
        )
        assert create_response.status_code == 201
        review_id = create_response.json()["id"]

        update_response = client.put(
            f"/api/reviews/weekly/{review_id}",
            json={"summary": "数学投入稳定，英语继续补弱"},
            headers=headers,
        )
        list_response = client.get("/api/reviews/weekly", headers=headers)

    assert update_response.status_code == 200
    assert update_response.json()["summary"] == "数学投入稳定，英语继续补弱"
    assert list_response.status_code == 200
    assert any(item["id"] == review_id for item in list_response.json())


def test_finish_timer_with_image_without_api_key_creates_analysis_placeholder() -> None:
    with TestClient(app) as client:
        headers = auth_headers(client)
        task_response = client.post(
            "/api/tasks",
            json={
                "plan_date": datetime.now(UTC).date().isoformat(),
                "subject": "math",
                "module": "advanced_math",
                "title": "定积分应用题",
                "task_type": "practice",
                "estimated_minutes": 90,
                "priority": 1,
            },
            headers=headers,
        )
        assert task_response.status_code == 201
        task_id = task_response.json()["id"]

        start_response = client.post("/api/timer/start", json={"task_id": task_id}, headers=headers)
        assert start_response.status_code == 201

        finish_response = client.post(
            "/api/timer/finish-with-images",
            data={"summary": "完成定积分应用题", "blockers": "", "quality": "medium"},
            files=[("files", ("problem.png", b"fake image bytes", "image/png"))],
            headers=headers,
        )

    assert finish_response.status_code == 200
    body = finish_response.json()
    assert body["record"]["title"] == "定积分应用题"
    assert len(body["images"]) == 1
    assert body["images"][0]["analysis_status"] == "skipped"


def test_upload_images_to_existing_record_and_generate_daily_review() -> None:
    now = datetime.now(UTC)
    with TestClient(app) as client:
        headers = auth_headers(client)
        record_response = client.post(
            "/api/records",
            json={
                "subject": "408",
                "module": "data_structure",
                "task_type": "manual",
                "title": "树的遍历错题",
                "started_at": (now - timedelta(minutes=45)).isoformat(),
                "ended_at": now.isoformat(),
                "duration_minutes": 45,
                "summary": "补录一组树遍历题",
                "quality": "medium",
            },
            headers=headers,
        )
        assert record_response.status_code == 201
        record_id = record_response.json()["id"]

        image_response = client.post(
            f"/api/records/{record_id}/images",
            files=[("files", ("tree.webp", b"fake webp bytes", "image/webp"))],
            headers=headers,
        )
        assert image_response.status_code == 200
        assert image_response.json()[0]["record_id"] == record_id

        review_response = client.post(
            f"/api/reviews/daily/generate?date={now.date().isoformat()}",
            headers=headers,
        )
        list_response = client.get(
            f"/api/reviews/daily?date={now.date().isoformat()}",
            headers=headers,
        )

    assert review_response.status_code == 200
    review = review_response.json()
    assert review["model_status"] == "fallback"
    assert "树的遍历错题" in review["completed_content"]
    assert list_response.status_code == 200
    assert len(list_response.json()) >= 1
