import sys
import pytest
from fastapi.testclient import TestClient

if sys.stdout and hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

from app.main import app
from app.services.state_machine import InterviewStage, interview_state_machine

client = TestClient(app)

def test_interview_state_machine_turns():
    """Verify 4-stage State Machine transitions based on turn count."""
    stage, is_fin = interview_state_machine.get_stage_for_turn(1)
    assert stage == InterviewStage.INTRO
    assert is_fin is False

    stage, is_fin = interview_state_machine.get_stage_for_turn(2)
    assert stage == InterviewStage.PORTFOLIO_DEEP_DIVE
    assert is_fin is False

    stage, is_fin = interview_state_machine.get_stage_for_turn(5)
    assert stage == InterviewStage.SITUATIONAL_CHALLENGE
    assert is_fin is False

    stage, is_fin = interview_state_machine.get_stage_for_turn(6)
    assert stage == InterviewStage.WRAP_UP
    assert is_fin is True

def test_api_session_state_machine_flow():
    """Verify FastAPI interview setup and answer endpoints return current_stage."""
    setup_res = client.post("/api/interview/setup", json={
        "target_school": "國立台灣大學",
        "target_major": "資訊工程學系"
    })
    assert setup_res.status_code == 200
    setup_data = setup_res.json()
    assert setup_data["current_stage"] == "INTRO"
    session_id = setup_data["session_id"]

    # Turn 2 submission
    ans_res = client.post("/api/interview/answer", json={
        "session_id": session_id,
        "user_answer": "我的優點是具備極強的自主學習與程式寫作能力。"
    })
    assert ans_res.status_code == 200
    ans_data = ans_res.json()
    assert ans_data["current_stage"] == "PORTFOLIO_DEEP_DIVE"
    assert ans_data["is_finished"] is False

if __name__ == "__main__":
    pytest.main(["-v", __file__])
