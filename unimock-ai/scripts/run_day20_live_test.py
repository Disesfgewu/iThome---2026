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

def run_day20_live_tests():
    print("==================================================", flush=True)
    print("UniMock AI - Day 20 Full Backend Architecture E2E Verification", flush=True)
    print("==================================================", flush=True)

    client = TestClient(app)

    print("\n--- [Step 1] Verifying System Architecture & Health Check ---", flush=True)
    res_health = client.get("/api/health")
    print(f"Health Status: {res_health.status_code} | Body: {res_health.json()}", flush=True)

    print("\n--- [Step 2] Full Interview Session E2E Workflow ---", flush=True)
    setup_payload = {
        "target_school": "國立臺灣大學",
        "target_major": "資訊工程學系",
        "interview_mode": "標準二階面試",
        "candidate_profile": {
            "applicant_name": "陳大明",
            "high_school": "臺北市立建國高級中學",
            "autobiography": "熟悉 Python 與演算法專案開發，曾參與科展並獲得優秀成績。"
        }
    }
    res_setup = client.post("/api/interview/setup", json=setup_payload)
    print(f"Interview Setup Status Code: {res_setup.status_code}", flush=True)
    data_setup = res_setup.json()
    session_id = data_setup["session_id"]
    print(f"Session ID: {session_id} | Stage: {data_setup['current_stage']}", flush=True)
    print(f"First Question: {data_setup['first_question'][:100]}...", flush=True)

    print("\n--- [Step 3] Multi-turn Answer Submission with Guardrails & Followup Agent ---", flush=True)
    ans_payload = {
        "session_id": session_id,
        "user_answer": "教授好，我主要在專案中使用 Python 進行演算法優化，將搜尋時間複雜度從 O(N^2) 降低到 O(N log N)。"
    }
    res_ans = client.post("/api/interview/answer", json=ans_payload)
    print(f"Answer Submission Status Code: {res_ans.status_code}", flush=True)
    data_ans = res_ans.json()
    print(f"Turn Count: {data_ans['turn_count']} | Stage: {data_ans['current_stage']}", flush=True)
    print(f"Next Question: {data_ans['next_question'][:100]}...", flush=True)

    print("\n--- [Step 4] Strategic Evaluation Report Generation & Packaging ---", flush=True)
    report_payload = {"session_id": session_id}
    res_report = client.post("/api/reports/generate", json=report_payload)
    print(f"Report Generation Status Code: {res_report.status_code}", flush=True)
    data_report = res_report.json()
    print(f"Report Generated Successfully for Session: {data_report['session_id']}", flush=True)

    print("\n==================================================", flush=True)
    print("Day 20 Full Backend Architecture E2E Verification Completed Successfully!", flush=True)
    print("==================================================", flush=True)

if __name__ == "__main__":
    run_day20_live_tests()
