import os
import sys
import asyncio

# Ensure UTF-8 output encoding for Windows PowerShell
if sys.stdout and hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.services.gemma_llm import gemma_client
from app.services.context_manager import token_context_guard
from app.services.security_guardrail import security_guardrail

async def run_day9_live_tests():
    print("==================================================", flush=True)
    print("UniMock AI - Day 9 Resilient Gemma Client & Token Guard Test", flush=True)
    print("==================================================", flush=True)

    # Test 1: Token Counting & Sliding-Window Context Truncation
    print("\n--- [Test 1] Token Count Estimation & Transcript Truncation ---", flush=True)
    long_lines = ["[系統]: 面試開始。"]
    for i in range(40):
        long_lines.append(f"[考官]: 請向我說明第 {i+1} 個專案遭遇的困難？")
        long_lines.append(f"[學生]: 在第 {i+1} 個專案中，我使用了 Python 與多流程架構，克服了複雜的極限瓶頸並成功解決難題。")
    
    long_transcript = "\n".join(long_lines)
    orig_tokens = token_context_guard.estimate_tokens(long_transcript)
    truncated_transcript = token_context_guard.truncate_transcript(long_transcript, max_tokens=300)
    trunc_tokens = token_context_guard.estimate_tokens(truncated_transcript)

    print(f"Original Transcript Length: {len(long_transcript)} chars (~{orig_tokens} tokens)", flush=True)
    print(f"Truncated Transcript Tokens: ~{trunc_tokens} tokens", flush=True)
    print("Truncated Transcript Output Snippet:\n", truncated_transcript[:250] + "...\n", flush=True)

    # Test 2: Resilient API Call with Context Window Protection
    print("--- [Test 2] Resilient Gemma-4-31B LLM Generation with Oversized Input Safeguard ---", flush=True)
    response = await gemma_client.invoke_with_system_prompt(
        prompt_name="question_generation",
        user_input="",
        target_school="國立台灣大學",
        target_major="資訊工程學系",
        interview_mode="頂大嚴謹模式",
        candidate_profile="高中代表隊參加全國軟體競賽一等獎，熱愛演算法與資安研究",
        sample_questions="範例問題：請向非資訊背景者解釋什麼是 Stack 與 Queue？",
        transcript=long_transcript  # Oversized transcript safely truncated by token guard!
    )
    print("Gemma Generated Question Response:\n", response, "\n", flush=True)

    # Test 3: Real-Time Async Token Streaming Output
    print("--- [Test 3] Real-Time Async Token Streaming Output (astream_with_system_prompt) ---", flush=True)
    print("Streamed Tokens: ", end="", flush=True)
    async for chunk in gemma_client.astream_with_system_prompt(
        prompt_name="response_generation",
        user_input="我選擇使用 Prepared Statements 來防止 SQL Injection 攻擊。",
        target_major="資訊工程學系",
        candidate_profile="高中資安社團社長，熟悉網路安全防禦",
        transcript="[系統]: 面試開始。[考官]: 請說明你曾處理過的資安案例？"
    ):
        print(chunk, end="", flush=True)
        await asyncio.sleep(0.01)
    print("\n\n==================================================", flush=True)
    print("Day 9 Live Protection & Streaming Test Completed Successfully!", flush=True)
    print("==================================================", flush=True)

if __name__ == "__main__":
    asyncio.run(run_day9_live_tests())
