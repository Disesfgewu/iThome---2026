import os
import sys
import asyncio
from fastapi.testclient import TestClient

if sys.stdout and hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.main import app

def run_day19_live_tests():
    print("==================================================", flush=True)
    print("UniMock AI - Day 19 API Pipeline Wire-Up Live Test", flush=True)
    print("==================================================", flush=True)

    client = TestClient(app)

    print("\n--- [Step 1] Verifying FastAPI Health Check Endpoint ---", flush=True)
    res_health = client.get("/api/health")
    print(f"Health Check Status Code: {res_health.status_code}", flush=True)
    print(f"Health Response: {res_health.json()}", flush=True)

    print("\n--- [Step 2] Testing Interview Session Setup & First Question ---", flush=True)
    setup_payload = {
        "target_school": "國立臺灣大學",
        "target_major": "資訊工程學系",
        "interview_mode": "標準二階面試",
        "candidate_profile": {
            "applicant_name": "王小明",
            "high_school": "臺北市立建國高級中學",
            "autobiography": "高中曾獲 APCS 大學程式設計先修檢測觀念 5 級、實作 4 級；參與科展榮獲佳作。"
        }
    }
    res_setup = client.post("/api/interview/setup", json=setup_payload)
    print(f"Interview Setup Status Code: {res_setup.status_code}", flush=True)
    data_setup = res_setup.json()
    session_id = data_setup["session_id"]
    print(f"Session Created: {session_id}", flush=True)
    print(f"Current Stage: {data_setup['current_stage']}", flush=True)
    print(f"First Question: {data_setup['first_question'][:100]}...", flush=True)

    print("\n--- [Step 3] Testing Session Records Retrieval Endpoint ---", flush=True)
    res_rec = client.get(f"/api/records/{session_id}")
    print(f"Records Status Code: {res_rec.status_code}", flush=True)
    print(f"Session ID in Record: {res_rec.json()['session_id']}", flush=True)

    print("\n==================================================", flush=True)
    print("Day 19 API Pipeline Wire-Up Live Test Completed Successfully!", flush=True)
    print("==================================================", flush=True)

if __name__ == "__main__":
    run_day19_live_tests()
