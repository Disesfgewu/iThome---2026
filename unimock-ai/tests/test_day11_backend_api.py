import os
import sys
import pytest
from fastapi.testclient import TestClient

if sys.stdout and hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

from app.main import app

client = TestClient(app)

def test_health_check_api():
    """Verify GET /api/health returns 200 OK and backend service status."""
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "online"
    assert data["model"] == "models/gemma-4-31b-it"

def test_interview_session_setup_and_flow():
    """Verify POST /api/interview/setup, POST /api/interview/answer, and record retrieval."""
    # 1. Setup Session
    setup_payload = {
        "target_school": "國立台灣大學",
        "target_major": "資訊工程學系",
        "interview_mode": "頂大嚴謹模式",
        "candidate_profile": {
            "target_school": "國立台灣大學",
            "target_major": "資訊工程學系",
            "autobiography": "代表隊成員，熱愛演算法開發。",
            "projects_and_awards": ["全國軟體競賽一等獎"]
        }
    }
    setup_res = client.post("/api/interview/setup", json=setup_payload)
    assert setup_res.status_code == 200
    setup_data = setup_res.json()
    session_id = setup_data["session_id"]
    assert len(session_id) > 0
    assert len(setup_data["first_question"].strip()) > 0

    # 2. Submit Answer
    answer_payload = {
        "session_id": session_id,
        "user_answer": "我會使用 Stack 實作復原 (Undo) 功能，因為後進先出的特性非常適合歷程復原。"
    }
    answer_res = client.post("/api/interview/answer", json=answer_payload)
    assert answer_res.status_code == 200
    answer_data = answer_res.json()
    assert answer_data["turn_count"] == 2
    assert len(answer_data["next_question"].strip()) > 0

    # 3. List Records
    records_res = client.get("/api/records/list")
    assert records_res.status_code == 200
    records_list = records_res.json()
    assert any(r["session_id"] == session_id for r in records_list)

    # 4. Detail Record
    detail_res = client.get(f"/api/records/{session_id}")
    assert detail_res.status_code == 200
    detail_data = detail_res.json()
    assert detail_data["target_major"] == "資訊工程學系"
    assert len(detail_data["transcript_turns"]) == 2

if __name__ == "__main__":
    pytest.main(["-v", __file__])
