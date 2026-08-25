import io
import sys
import pytest
from pypdf import PdfWriter
from fastapi.testclient import TestClient
from app.main import app

if sys.stdout and hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

client = TestClient(app)

def create_valid_pdf_bytes() -> bytes:
    """Generates valid 1-page PDF binary bytes for test upload."""
    writer = PdfWriter()
    writer.add_blank_page(width=200, height=200)
    pdf_stream = io.BytesIO()
    writer.write(pdf_stream)
    return pdf_stream.getvalue()

def test_backend_health_and_architecture():
    """Verify backend health endpoint and model service alignment."""
    res = client.get("/api/health")
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "online"
    assert data["model"] == "models/gemma-4-31b-it"
    assert data["embedding_model"] == "models/gemini-embedding-2"

def test_resume_upload_endpoint():
    """Verify PDF resume upload endpoint and profile extraction."""
    valid_pdf_bytes = create_valid_pdf_bytes()
    response = client.post(
        "/api/resume/upload-pdf",
        files={"file": ("resume.pdf", io.BytesIO(valid_pdf_bytes), "application/pdf")},
        data={"target_school": "國立臺灣大學", "target_major": "資訊工程學系"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "candidate_profile" in data
    assert data["candidate_profile"]["target_major"] == "資訊工程學系"

def test_full_interview_lifecycle_e2e():
    """
    Comprehensive E2E test verifying full backend lifecycle:
    1. Interview Setup
    2. Multi-turn Dialogue Answer Submission
    3. Session Records Retrieval
    """
    # 1. Setup Session
    setup_payload = {
        "target_school": "國立臺灣大學",
        "target_major": "資訊工程學系",
        "interview_mode": "標準二階面試",
        "candidate_profile": {
            "applicant_name": "陳大明",
            "high_school": "臺北市立建國高級中學",
            "autobiography": "高中時期熟悉 Python，開發過機器學習圖形辨識專案與二元搜尋樹演算法。"
        }
    }
    res_setup = client.post("/api/interview/setup", json=setup_payload)
    assert res_setup.status_code == 200
    data_setup = res_setup.json()
    session_id = data_setup["session_id"]
    assert data_setup["current_stage"] == "INTRO"
    assert len(data_setup["first_question"]) > 0

    # 2. Submit Answer Turn 1
    answer_payload = {
        "session_id": session_id,
        "user_answer": "教授好，我高中的專案是基於 OpenCV 與 Python 實作機器學習影像分類，主要為解決演算法效率瓶頸。"
    }
    res_ans = client.post("/api/interview/answer", json=answer_payload)
    assert res_ans.status_code == 200
    data_ans = res_ans.json()
    assert "next_question" in data_ans
    assert data_ans["turn_count"] >= 1

    # 3. Session Record Retrieval
    res_rec = client.get(f"/api/records/{session_id}")
    assert res_rec.status_code == 200
    data_rec = res_rec.json()
    assert data_rec["session_id"] == session_id
    assert len(data_rec["transcript_turns"]) >= 1

if __name__ == "__main__":
    pytest.main(["-v", __file__])
