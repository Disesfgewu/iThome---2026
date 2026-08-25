import sys
import pytest
from app.services.report_generator import report_generator

if sys.stdout and hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

def test_format_export_package():
    """Verify formatting strategic evaluation export JSON package."""
    mock_session = {
        "session_id": "test_day17_sess",
        "target_school": "國立臺灣大學",
        "target_major": "資訊工程學系",
        "interview_mode": "標準二階面試",
        "transcript_turns": [{"question": "Q1", "answer": "A1"}],
        "created_at": "2026-08-25T20:00:00Z"
    }
    mock_eval = {
        "overall_score": 88.0,
        "radar_scores": {"logic_structure": 4.5, "major_relevance": 5.0, "communication_clarity": 4.0, "adaptability": 4.5},
        "scoring_evaluation_text": "邏輯嚴謹，展現跨領域優勢",
        "overall_strategic_report": "表現優異"
    }

    pkg = report_generator.format_export_package(mock_session, mock_eval)
    assert pkg["session_id"] == "test_day17_sess"
    assert pkg["overall_score"] == 88.0
    assert pkg["pi_shaped_talent_analysis"]["has_cross_disciplinary_experience"] is True

if __name__ == "__main__":
    pytest.main(["-v", __file__])
