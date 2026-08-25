import os
import sys
import asyncio
from httpx import AsyncClient, ASGITransport

if sys.stdout and hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.main import app
from app.services.memory_manager import memory_manager

async def run_day14_live_tests():
    print("==================================================", flush=True)
    print("UniMock AI - Day 14 LangChain Memory Live Test", flush=True)
    print("==================================================", flush=True)

    print("\n--- [Step 1] Verifying LangChain ConversationTokenBufferMemory ---", flush=True)
    session_id = "live_sess_day14_test"
    memory_manager.clear_memory(session_id)

    memory_manager.add_ai_message(session_id, "你好，歡迎參加資工系模擬面試。")
    memory_manager.add_user_message(session_id, "教授好，我主要研究演算法優化與系統開發。")
    buffer = memory_manager.get_buffer_string(session_id)
    print(f"Memory Buffer String:\n{buffer}\n", flush=True)

    print("--- [Step 2] Live FastAPI Session LangChain Memory Integration ---", flush=True)
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # 1. Setup Session
        res = await client.post("/api/interview/setup", json={
            "target_school": "國立陽明交通大學",
            "target_major": "資訊工程學系",
            "interview_mode": "標準二階面試"
        })
        sess_data = res.json()
        active_sess_id = sess_data["session_id"]
        print(f"Session Created: {active_sess_id} | Memory Initialized.", flush=True)

        # 2. Submit Answer 1
        res = await client.post("/api/interview/answer", json={
            "session_id": active_sess_id,
            "user_answer": "教授好，我對陽明交大資工系非常有熱情，高中曾參與競賽與專案優化。"
        })
        ans_data = res.json()
        print(f"\nQ2 Generated with Memory Context:\n{ans_data['next_question']}\n", flush=True)

    print("==================================================", flush=True)
    print("Day 14 LangChain Memory Live Test Completed Successfully!", flush=True)
    print("==================================================", flush=True)

if __name__ == "__main__":
    asyncio.run(run_day14_live_tests())
