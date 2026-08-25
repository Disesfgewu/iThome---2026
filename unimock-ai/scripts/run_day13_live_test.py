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
from app.services.followup_agent import followup_agent

async def run_day13_live_tests():
    print("==================================================", flush=True)
    print("UniMock AI - Day 13 Socratic Followup Optimization Live Test", flush=True)
    print("==================================================", flush=True)

    print("\n--- [Step 1] Verifying FollowupAgent Quality Evaluation ---", flush=True)
    brief_answer = "我喜歡寫程式。"
    quality = followup_agent.evaluate_answer_quality(brief_answer)
    print(f"Brief Answer Evaluation: Length={quality['length']} | Too Brief={quality['is_too_brief']} | Socratic Probe Needed={quality['requires_socratic_probe']}", flush=True)

    complete_answer = "教授好，我採用 Python 與 C++ 開發軟體專案，透過演算法優化將記憶體開銷縮短 40%，獲得競賽一等獎。"
    quality_complete = followup_agent.evaluate_answer_quality(complete_answer)
    print(f"Complete Answer Evaluation: Length={quality_complete['length']} | STAR Score={quality_complete['star_score']} | Socratic Probe Needed={quality_complete['requires_socratic_probe']}", flush=True)

    print("\n--- [Step 2] Live FastAPI Socratic Followup Triggering ---", flush=True)
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # 1. Setup Session
        res = await client.post("/api/interview/setup", json={
            "target_school": "國立清華大學",
            "target_major": "資訊工程學系",
            "interview_mode": "標準二階面試"
        })
        session_data = res.json()
        session_id = session_data["session_id"]
        print(f"Session Created: {session_id} | First Question Generated.", flush=True)

        # 2. Submit Brief Vague Answer (Triggers Socratic Probe)
        res = await client.post("/api/interview/answer", json={
            "session_id": session_id,
            "user_answer": "就寫程式。"
        })
        ans_data = res.json()
        print(f"\nSocratic Follow-up Question Generated:\n{ans_data['next_question']}\n", flush=True)

    print("==================================================", flush=True)
    print("Day 13 Socratic Followup Live Test Completed Successfully!", flush=True)
    print("==================================================", flush=True)

if __name__ == "__main__":
    asyncio.run(run_day13_live_tests())
