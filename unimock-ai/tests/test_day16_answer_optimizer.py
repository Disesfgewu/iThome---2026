import sys
import pytest
from app.services.answer_optimizer import answer_optimizer

if sys.stdout and hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

def test_answer_optimizer_service_initialization():
    """Verify AnswerOptimizerService object structure and methods."""
    assert hasattr(answer_optimizer, "diagnose_and_optimize_turn")
    assert hasattr(answer_optimizer, "batch_diagnose_transcript")

if __name__ == "__main__":
    pytest.main(["-v", __file__])
