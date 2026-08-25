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

async def run_day11_live_api_tests():
    print("==================================================", flush=True)
    print("UniMock AI - Day 11 FastAPI Backend Live API Integration Test", flush=True)
    print("==================================================", flush=True)

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # Test 1: Health Check
        print("\n--- [Test 1] Health Check Endpoint ---", flush=True)
        res = await client.get("/api/health")
        print(f"Health Check Status Code: {res.status_code}", flush=True)
        print(f"Health Response: {res.json()}", flush=True)

        # Test 2: Interview Setup
        print("\n--- [Test 2] Interview Setup Endpoint ---", flush=True)
        setup_payload = {
            "target_school": "國立台灣大學",
            "target_major": "資訊工程學系",
            "interview_mode": "頂大嚴謹模式",
            "candidate_profile": {
                "target_school": "國立台灣大學",
                "target_major": "資訊工程學系",
                "autobiography": "我是熱愛演算法與系統開發的高中代表隊成員。",
                "projects_and_awards": ["全國資訊軟體競賽一等獎", "APCS 觀念4級實作5級"],
                "certifications_and_skills": ["Python", "C++", "Data Structures"]
            }
        }
        res = await client.post("/api/interview/setup", json=setup_payload)
        print(f"Setup Status Code: {res.status_code}", flush=True)
        setup_data = res.json()
        session_id = setup_data["session_id"]
        print(f"Session Created: {session_id}", flush=True)
        print(f"First Question Generated:\n{setup_data['first_question']}", flush=True)

        # Test 3: Answer Submission & Follow-up Question
        print("\n--- [Test 3] Answer Submission Endpoint ---", flush=True)
        answer_payload = {
            "session_id": session_id,
            "user_answer": "教授好，我會選擇使用 Stack 實作復原 (Ctrl+Z) 與重做 (Ctrl+Y) 功能。Stack 是後進先出的資料結構，就像疊盤子一樣..."
        }
        res = await client.post("/api/interview/answer", json=answer_payload)
        print(f"Answer Status Code: {res.status_code}", flush=True)
        answer_data = res.json()
        print(f"Next Question Generated:\n{answer_data['next_question']}", flush=True)

        # Test 4: Report Generation
        print("\n--- [Test 4] Evaluation Report Generation Endpoint ---", flush=True)
        report_payload = {"session_id": session_id}
        res = await client.post("/api/reports/generate", json=report_payload)
        print(f"Report Status Code: {res.status_code}", flush=True)
        report_data = res.json()
        print(f"Strategic Report Snippet:\n{report_data['overall_strategic_report'][:300]}...", flush=True)

        # Test 5: Session Record Retrieval
        print("\n--- [Test 5] Record Listing & Detail Endpoint ---", flush=True)
        res = await client.get("/api/records/list")
        print(f"Record List Count: {len(res.json())}", flush=True)
        res = await client.get(f"/api/records/{session_id}")
        print(f"Record Detail Turns: {len(res.json()['transcript_turns'])} turns", flush=True)

    print("\n==================================================", flush=True)
    print("Day 11 FastAPI Backend Test Completed Successfully!", flush=True)
    print("==================================================", flush=True)

if __name__ == "__main__":
    asyncio.run(run_day11_live_api_tests())
