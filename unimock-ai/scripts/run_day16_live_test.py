import os
import sys
import asyncio

if sys.stdout and hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.services.answer_optimizer import answer_optimizer

async def run_day16_live_tests():
    print("==================================================", flush=True)
    print("UniMock AI - Day 16 Per-Question Weakness Diagnosis Live Test", flush=True)
    print("==================================================", flush=True)

    question = "請說明的專案作品中，在演算法優化部分遭遇的最難技術卡關是什麼？"
    user_answer = "我就寫程式，遇到了 Bug 就上 Google 搜尋，把它修好。"
    target_major = "資訊工程學系"

    print("\n--- [Step 1] Diagnosing Candidate Answer Weakness via Gemma-4-31B ---", flush=True)
    res = await answer_optimizer.diagnose_and_optimize_turn(question, user_answer, target_major)

    print(f"Question: {res['question']}", flush=True)
    print(f"Candidate Original Answer: {res['original_answer']}\n", flush=True)
    print("Diagnosis & High-scoring Exemplar Answer Generated:")
    print(res["diagnosis_and_optimized_answer"], flush=True)

    print("\n==================================================", flush=True)
    print("Day 16 Per-Question Weakness Diagnosis Live Test Completed Successfully!", flush=True)
    print("==================================================", flush=True)

if __name__ == "__main__":
    asyncio.run(run_day16_live_tests())
