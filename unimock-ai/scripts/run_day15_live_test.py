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
from app.services.evaluation_service import evaluation_service

async def run_day15_live_tests():
    print("==================================================", flush=True)
    print("UniMock AI - Day 15 Evaluation & Radar Scoring Live Test", flush=True)
    print("==================================================", flush=True)

    print("\n--- [Step 1] Verifying EvaluationService Radar Score Parsing ---", flush=True)
    sample_text = (
        "【四大維度評分】\n"
        "1. 邏輯與結構性：4 星 - 採用 STAR 原則，邏輯清晰\n"
        "2. 專業契合度：5 星 - 精確使用演算法與系統開發專業術語\n"
        "3. 表達與溝通流暢度：4 星 - 口條流暢，敘述有條理\n"
        "4. 應變與抗壓韌性：4 星 - 能正面回應追問細節\n"
    )
    radar = evaluation_service.parse_radar_scores(sample_text)
    print(f"Parsed Radar Scores:\n  - Logic & Structure: {radar['logic_structure']} / 5.0")
    print(f"  - Major Relevance: {radar['major_relevance']} / 5.0")
    print(f"  - Communication Clarity: {radar['communication_clarity']} / 5.0")
    print(f"  - Adaptability: {radar['adaptability']} / 5.0\n", flush=True)

    print("--- [Step 2] Live FastAPI Strategic Report Generation ---", flush=True)
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # 1. Setup Session
        res = await client.post("/api/interview/setup", json={
            "target_school": "國立臺灣大學",
            "target_major": "資訊工程學系",
            "interview_mode": "標準二階面試"
        })
        sess_data = res.json()
        active_sess_id = sess_data["session_id"]
        print(f"Session Created: {active_sess_id}", flush=True)

        # 2. Submit Answer
        await client.post("/api/interview/answer", json={
            "session_id": active_sess_id,
            "user_answer": "教授好，我對台大資工系非常有興趣，高中曾主導演算法專案開發，採用 C++ 實作複雜度 O(N log N) 的排序與搜尋優化。"
        })

        # 3. Generate Report
        print("Generating Strategic Evaluation Report via Gemma-4-31B...", flush=True)
        rep_res = await client.post("/api/reports/generate", json={
            "session_id": active_sess_id
        })
        report_data = rep_res.json()
        print(f"Report Generated Successfully for Session: {report_data['session_id']}", flush=True)
        print(f"Scoring Evaluation Snippet:\n{report_data['scoring_evaluation'][:300]}...\n", flush=True)

    print("==================================================", flush=True)
    print("Day 15 Evaluation & Radar Scoring Live Test Completed Successfully!", flush=True)
    print("==================================================", flush=True)

if __name__ == "__main__":
    asyncio.run(run_day15_live_tests())
