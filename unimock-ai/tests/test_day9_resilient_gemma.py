import os
import sys
import pytest
import asyncio

# Reconfigure stdout for Windows console UTF-8 support
if sys.stdout and hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

from app.services.gemma_llm import GemmaLLMClient, gemma_client
from app.services.context_manager import token_context_guard, TokenContextGuard

def test_token_estimation_and_truncation():
    """Verify TokenContextGuard estimates token count and sliding-window truncates long transcript."""
    guard = TokenContextGuard(max_context_tokens=1000)
    
    sample_text = "教授好，我是學生小明，我熱愛資訊科學與演算法研習。"
    tokens = guard.estimate_tokens(sample_text)
    assert tokens > 0
    
    # Create an excessively long transcript to test truncation
    long_lines = ["[系統]: 面試開始。"]
    for i in range(50):
        long_lines.append(f"[考官]: 請說明第 {i+1} 個專案細節與挑戰？")
        long_lines.append(f"[學生]: 在第 {i+1} 個專案中，我使用了大量演算法與資料結構，並進行了重構與優化...")
    
    long_transcript = "\n".join(long_lines)
    truncated = guard.truncate_transcript(long_transcript, max_tokens=300)
    
    assert "記憶摘要壓縮" in truncated
    assert guard.estimate_tokens(truncated) < guard.estimate_tokens(long_transcript)

def test_resilient_gemma_client_retries_and_stream():
    """Verify GemmaLLMClient resilience settings and async streaming output."""
    assert gemma_client.max_retries == 3
    assert gemma_client.base_backoff_delay == 2.0

    async def _test_streaming():
        tokens_received = []
        async for chunk in gemma_client.astream_with_system_prompt(
            prompt_name="question_generation",
            user_input="",
            target_school="國立台灣大學",
            target_major="資訊工程學系",
            interview_mode="標準面試",
            candidate_profile="高中代表隊參加全國軟體競賽一等獎",
            sample_questions="範例題目：請說明 Stack 與 Queue 的差異？",
            transcript="[系統]: 面試開始。"
        ):
            tokens_received.append(chunk)

        assert len(tokens_received) > 0
        full_streamed_text = "".join(tokens_received)
        assert len(full_streamed_text.strip()) > 0
        safe_preview = full_streamed_text[:100].encode("ascii", "ignore").decode("ascii") or "Streaming OK"
        print(f"\n[Async Token Stream Output Preview]: {safe_preview}")

    asyncio.run(_test_streaming())

if __name__ == "__main__":
    pytest.main(["-v", __file__])
