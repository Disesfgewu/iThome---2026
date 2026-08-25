import sys
import pytest
from app.services.memory_manager import memory_manager

if sys.stdout and hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

def test_langchain_memory_addition_and_buffer():
    """Verify adding messages to ConversationTokenBufferMemory and getting buffer string."""
    session_id = "test_sess_langchain_001"
    memory_manager.clear_memory(session_id)

    # 1. Add AI initial question
    memory_manager.add_ai_message(session_id, "你好，歡迎參加面試，請簡單自我介紹。")
    buffer_str = memory_manager.get_buffer_string(session_id)
    assert "自我介紹" in buffer_str

    # 2. Add User answer
    memory_manager.add_user_message(session_id, "教授好，我對資工領域非常有興趣，主修演算法優化。")
    buffer_str = memory_manager.get_buffer_string(session_id)
    assert "演算法優化" in buffer_str

    # 3. Clear memory
    memory_manager.clear_memory(session_id)
    assert len(memory_manager.get_buffer_string(session_id)) == 0

if __name__ == "__main__":
    pytest.main(["-v", __file__])
