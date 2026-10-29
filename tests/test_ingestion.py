from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health_endpoint():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_hospitals_endpoint():
    response = client.get("/api/hospitals")
    assert response.status_code == 200
    assert "items" in response.json()


def test_analytics_overview_endpoint():
    response = client.get("/api/analytics/overview")
    assert response.status_code == 200
    assert "total_hospitals" in response.json()


def test_import_preview_endpoint():
    csv_data = "hospital_id,hospital_name,governorate,total_beds,occupied_beds\nH-1,Test Hospital,Cairo,200,80\n"
    response = client.post(
        "/api/import/preview",
        files={"file": ("sample.csv", csv_data, "text/csv")},
    )
    assert response.status_code == 200
    assert response.json()["file_name"] == "sample.csv"


def test_ai_assistant_query():
    response = client.post("/api/assistant/query", json={"question": "Which hospitals have high occupancy?"})
    assert response.status_code == 200
    assert "answer" in response.json()
