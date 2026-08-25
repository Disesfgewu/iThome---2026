import os
import sys
import asyncio

if sys.stdout and hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.services.report_generator import report_generator
from app.services.evaluation_service import evaluation_service

async def run_day17_live_tests():
    print("==================================================", flush=True)
    print("UniMock AI - Day 17 Comprehensive Report & Pi-Shaped Talent Live Test", flush=True)
    print("==================================================", flush=True)

    print("\n--- [Step 1] Verifying Pi-Shaped Cross-disciplinary Prompt Integration ---", flush=True)
    transcript = (
        "[考官]: 你在高中曾修讀跨領域生醫資訊與 Python 機器學習課程，請分享你的跨領域學習體驗。\n"
        "[學生]: 教授好，我主修演算法，同時跨修了生物資訊學，將機器學習應用於蛋白質結構預測，展現跨領域 π 型整合能力。"
    )

    print("Evaluating Session with Pi-Shaped Cross-disciplinary Focus via Gemma-4-31B...", flush=True)
    eval_res = await evaluation_service.evaluate_interview_session(
        session_id="live_sess_day17_pishaped",
        target_school="國立臺灣大學",
        target_major="資訊工程學系",
        candidate_profile_text="【修課/經歷】：跨領域生醫資訊專題，機器學習與演算法優化。",
        transcript_text=transcript
    )

    print(f"Overall Score Calculated: {eval_res['overall_score']} / 100", flush=True)
    print("Radar Scores:", eval_res["radar_scores"], flush=True)

    print("\n--- [Step 2] Packaging Export Package ---", flush=True)
    mock_sess = {
        "session_id": "live_sess_day17_pishaped",
        "target_school": "國立臺灣大學",
        "target_major": "資訊工程學系",
        "interview_mode": "標準二階面試",
        "transcript_turns": [{"question": "Q1", "answer": "A1"}],
        "created_at": "2026-08-25T20:00:00Z"
    }
    pkg = report_generator.format_export_package(mock_sess, eval_res)
    print(f"Export Package Formatted Successfully for Session: {pkg['session_id']}", flush=True)
    print(f"Pi-Shaped Note: {pkg['pi_shaped_talent_analysis']['note']}", flush=True)

    print("\n==================================================", flush=True)
    print("Day 17 Comprehensive Report Live Test Completed Successfully!", flush=True)
    print("==================================================", flush=True)

if __name__ == "__main__":
    asyncio.run(run_day17_live_tests())
