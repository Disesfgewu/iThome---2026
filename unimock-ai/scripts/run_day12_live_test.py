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
from app.services.state_machine import InterviewStage, interview_state_machine

async def run_day12_live_tests():
    print("==================================================", flush=True)
    print("UniMock AI - Day 12 Interview State Machine Live Test", flush=True)
    print("==================================================", flush=True)

    print("\n--- [Step 1] Verifying 4-Stage State Machine Transition Rules ---", flush=True)
    for turn in range(1, 7):
        stage, is_fin = interview_state_machine.get_stage_for_turn(turn)
        print(f"  - Turn {turn}: Stage = {stage.value} | Finished = {is_fin}", flush=True)

    print("\n--- [Step 2] Live FastAPI Session State Machine Dialogue Flow ---", flush=True)
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # Setup Session
        res = await client.post("/api/interview/setup", json={
            "target_school": "國立成功大學",
            "target_major": "資訊工程學系",
            "interview_mode": "標準二階面試"
        })
        session_data = res.json()
        session_id = session_data["session_id"]
        print(f"Session Created: {session_id} | Stage: {session_data['current_stage']}", flush=True)
        print(f"Q1 (INTRO):\n{session_data['first_question'][:150]}...\n", flush=True)

        # Answer 1 (Moves to PORTFOLIO_DEEP_DIVE)
        res = await client.post("/api/interview/answer", json={
            "session_id": session_id,
            "user_answer": "教授好，我對貴系非常有熱情，高中曾參與軟體專案開發與競賽，主要研究資料結構優化與系統效能改善..."
        })
        ans_data = res.json()
        print(f"Q2 ({ans_data['current_stage']}):\n{ans_data['next_question'][:150]}...\n", flush=True)

    print("==================================================", flush=True)
    print("Day 12 State Machine Live Test Completed Successfully!", flush=True)
    print("==================================================", flush=True)

if __name__ == "__main__":
    asyncio.run(run_day12_live_tests())
