import sys
import pytest
from app.services.evaluation_service import evaluation_service

if sys.stdout and hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

def test_parse_radar_scores():
    """Verify parsing 4-dimension star ratings from LLM scoring text."""
    sample_text = (
        "【四大維度評分】\n"
        "1. 邏輯與結構性：4 星 - STAR 原則完整\n"
        "2. 專業契合度：5 星 - 術語精準\n"
        "3. 表達與溝通流暢度：3 星 - 稍微緊張\n"
        "4. 應變與抗壓韌性：4 星 - 回答迅速\n"
    )
    scores = evaluation_service.parse_radar_scores(sample_text)
    assert scores["logic_structure"] == 8.0
    assert scores["major_relevance"] == 10.0
    assert scores["communication_clarity"] == 6.0
    assert scores["adaptability"] == 8.0

if __name__ == "__main__":
    pytest.main(["-v", __file__])
