import sys
import pytest
from fastapi.testclient import TestClient
from app.main import app

if sys.stdout and hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

client = TestClient(app)

def test_api_health_check():
    """Verify backend API health check endpoint."""
    res = client.get("/api/health")
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "online"
    assert "gemma-4-31b-it" in data["model"]

def test_full_session_creation_flow():
    """Verify session creation and interview setup endpoint."""
    setup_payload = {
        "target_school": "國立臺灣大學",
        "target_major": "資訊工程學系",
        "interview_mode": "標準二階面試",
        "candidate_profile": {
            "applicant_name": "王小明",
            "high_school": "臺北市立建國高級中學",
            "autobiography": "熟悉 Python 與演算法。"
        }
    }
    res = client.post("/api/interview/setup", json=setup_payload)
    assert res.status_code == 200
    data = res.json()
    assert "session_id" in data
    assert "first_question" in data
    assert data["current_stage"] == "INTRO"

if __name__ == "__main__":
    pytest.main(["-v", __file__])
