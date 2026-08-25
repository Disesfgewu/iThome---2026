import sys
import pytest
from app.services.followup_agent import followup_agent

if sys.stdout and hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

def test_brief_answer_evaluation():
    """Verify FollowupAgent flags brief answers and triggers Socratic probe."""
    brief_answer = "我喜歡寫程式。"
    eval_res = followup_agent.evaluate_answer_quality(brief_answer)
    assert eval_res["is_too_brief"] is True
    assert eval_res["requires_socratic_probe"] is True

    instruction = followup_agent.build_socratic_prompt("請自我介紹", brief_answer, eval_res)
    assert "回答過於簡短" in instruction
    assert "為什麼" in instruction or "How" in instruction

def test_complete_answer_evaluation():
    """Verify FollowupAgent passes complete STAR answers."""
    complete_answer = "教授好，我採用 Python 與 C++ 開發軟體專案，透過演算法優化將記憶體開銷縮短 40%，獲得競賽一等獎。"
    eval_res = followup_agent.evaluate_answer_quality(complete_answer)
    assert eval_res["is_too_brief"] is False
    assert eval_res["has_action"] is True
    assert eval_res["has_result"] is True
    assert eval_res["star_score"] == 3

if __name__ == "__main__":
    pytest.main(["-v", __file__])
