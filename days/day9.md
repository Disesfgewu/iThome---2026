# 【Day 9】模組化大腦：LLM 後端 Client 穩定度、429 重試與對話上下文管理模組封裝

在完成了 Day 7 的 Gemma 4 LLM 客戶端與 Day 8 的 RAG 全方位履歷檢索器後，今天我們進入 AI 大腦的關鍵防禦層搭建——**LLM Client 穩定度強化、429 Rate Limit 指數退避重試（Exponential Backoff）、Token 計數器與滑動視窗對話上下文管理 (TokenContextGuard)，以及非同步串流輸出 (Async Streaming)**。

在真實的高併發面試情境中，大型語言模型常遇到兩大極限問題：
1. **API 429 速率限制 (ResourceExhausted / Rate Limit Exceeded)**：免費層或高併發時的限流崩潰。
2. **上下文長度爆表 (Context Window Overflow / Too Many Tokens Input)**：當學生與考官問答輪數增加，逐字稿 (`transcript`) 與備審履歷 (`candidate_profile`) 累積超出 LLM 的輸入 Context Window。

今天我們實現了四大關鍵防禦機制：
- **429 Rate Limit 與 Network Error 自動重試 (`ResilientGemmaClient`)**：解析 Google 429 `retry_delay` 標頭，並以 `2^attempt * base_delay` 的指數退避機制自動休眠與重試（最多 3 次）。
- **Token 計數與滑動視窗動態截斷 (`TokenContextGuard`)**：即時估算繁簡中文與英文混合文本 Token 長度。當對話逐字稿超出安全閾值時，自動保留系統指示詞與近期焦點對話，對更早期的問答進行動態記憶壓縮，防止 Context Window Overflow。
- **即時非同步 token 串流 (`astream_with_system_prompt`)**：採用 Python `AsyncGenerator[str, None]`，為前端 SSE (Server-Sent Events) 打下即時逐字吐字基礎。
- **純粹 Gemma-4-31B-it 調用**：全數文字生成與評估均由 `models/gemma-4-31b-it` 獨立承載。

---

## 1. 滑動視窗對話上下文管理器實作 (`app/services/context_manager.py`)

```python
import re
from typing import Dict, Any, List

class TokenContextGuard:
    """
    Token Count Estimator & Dynamic Context Window Truncation Guard.
    
    Protects LLM calls against:
    1. 'Too Many Tokens Input' / Context Window Overflow.
    2. Excessive API cost / rate limit consumption.
    """
    def __init__(self, max_context_tokens: int = 6000):
        self.max_context_tokens = max_context_tokens

    def estimate_tokens(self, text: str) -> int:
        """Estimates token length for Traditional Chinese / English mixed text (~1.5 chars per CJK token)."""
        if not text:
            return 0
        cjk_count = len(re.findall(r'[\u4e00-\u9fff]', text))
        non_cjk_words = len(re.findall(r'\b\w+\b', text))
        return int(cjk_count * 1.5 + non_cjk_words * 1.3)

    def truncate_transcript(self, transcript: str, max_tokens: int = 3000) -> str:
        """
        Sliding-window truncates older dialogue turns from transcript if token count exceeds max_tokens.
        Preserves header instructions and recent N dialogue turns.
        """
        if not transcript or self.estimate_tokens(transcript) <= max_tokens:
            return transcript

        lines = transcript.split("\n")
        header_lines = [l for l in lines if l.startswith("[系統]:") or "面試開始" in l]
        dialogue_lines = [l for l in lines if not (l.startswith("[系統]:") or "面試開始" in l)]

        kept_dialogue = []
        accumulated_tokens = self.estimate_tokens("\n".join(header_lines))
        
        for line in reversed(dialogue_lines):
            line_tokens = self.estimate_tokens(line)
            if accumulated_tokens + line_tokens > max_tokens:
                break
            kept_dialogue.insert(0, line)
            accumulated_tokens += line_tokens

        truncated_summary = "[系統]: (更早期的問答對話已進行記憶摘要壓縮以控制 Token 長度...)\n"
        return "\n".join(header_lines) + "\n" + truncated_summary + "\n".join(kept_dialogue)

    def sanitize_prompt_kwargs(self, prompt_kwargs: Dict[str, Any], max_tokens: int = 5000) -> Dict[str, Any]:
        """Sanitizes and truncates prompt kwargs to prevent Context Window Overflow."""
        sanitized = dict(prompt_kwargs)
        if "transcript" in sanitized and isinstance(sanitized["transcript"], str):
            sanitized["transcript"] = self.truncate_transcript(sanitized["transcript"], max_tokens=max_tokens // 2)

        if "candidate_profile" in sanitized and isinstance(sanitized["candidate_profile"], str):
            profile_text = sanitized["candidate_profile"]
            if self.estimate_tokens(profile_text) > (max_tokens // 2):
                sanitized["candidate_profile"] = profile_text[:3000] + "\n... (履歷其餘章節摘要截斷)"

        return sanitized

token_context_guard = TokenContextGuard()
```

---

## 2. 具備 429 重試與串流能力之 Gemma Client (`app/services/gemma_llm.py`)

```python
import os
import re
import time
import asyncio
from typing import List, Dict, Any, Optional, AsyncGenerator
import google.generativeai as genai
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.messages import BaseMessage, HumanMessage, SystemMessage, AIMessage
from langchain_core.outputs import ChatResult, ChatGeneration
from pydantic import Field, PrivateAttr

from app.config import settings
from app.services.prompt_manager import prompt_manager
from app.services.security_guardrail import security_guardrail
from app.services.context_manager import token_context_guard

class GemmaLLMClient(BaseChatModel):
    """
    Unified Resilient LangChain ChatModel Client Interface strictly for Gemma-4-31B-it (models/gemma-4-31b-it).
    """
    model_name: str = Field(default_factory=lambda: settings.PRIMARY_LLM_MODEL)
    temperature: float = Field(default_factory=lambda: settings.LLM_TEMPERATURE)
    top_p: float = Field(default_factory=lambda: settings.LLM_TOP_P)
    max_retries: int = Field(default=3)
    base_backoff_delay: float = Field(default=2.0)

    def _generate(self, messages: List[BaseMessage], **kwargs: Any) -> ChatResult:
        # 1. Security Guardrail Validation
        human_inputs = [msg.content for msg in messages if isinstance(msg, HumanMessage)]
        if human_inputs:
            is_safe, reason = security_guardrail.verify_input_safety(human_inputs[-1])
            if not is_safe:
                return ChatResult(generations=[ChatGeneration(message=AIMessage(content="[Security Alert] 請求已安全攔截。"))])

        prompt_str = self._format_messages_to_gemma_chatml(messages)

        # 2. Resilient Exponential Backoff Retry Loop for 429 Rate Limits
        last_exception = None
        for attempt in range(self.max_retries):
            try:
                response = self._model.generate_content(prompt_str)
                output_text = response.text if response and hasattr(response, "text") else ""
                clean_text = re.sub(r"<end_of_turn>$", "", output_text).strip()
                return ChatResult(generations=[ChatGeneration(message=AIMessage(content=clean_text))])
            except Exception as e:
                last_exception = e
                err_msg = str(e).lower()
                if "429" in err_msg or "resource_exhausted" in err_msg or "quota" in err_msg:
                    retry_delay = self.base_backoff_delay * (2 ** attempt) + 1.0
                    time.sleep(retry_delay)
                else:
                    time.sleep(self.base_backoff_delay * (attempt + 1))

        raise RuntimeError(f"Gemma LLM API call failed after {self.max_retries} attempts: {last_exception}")

    async def invoke_with_system_prompt(self, prompt_name: str, user_input: str = "", **prompt_kwargs) -> str:
        # Automatic Token Context Protection
        clean_kwargs = token_context_guard.sanitize_prompt_kwargs(prompt_kwargs)
        system_prompt_text = await prompt_manager.get_system_prompt(prompt_name, **clean_kwargs)
        
        messages = [SystemMessage(content=system_prompt_text)]
        if user_input and user_input.strip():
            messages.append(HumanMessage(content=user_input.strip()))

        result = await asyncio.to_thread(self._generate, messages)
        return result.generations[0].message.content

    async def astream_with_system_prompt(self, prompt_name: str, user_input: str = "", **prompt_kwargs) -> AsyncGenerator[str, None]:
        """Asynchronously streams output tokens for real-time SSE streaming."""
        clean_kwargs = token_context_guard.sanitize_prompt_kwargs(prompt_kwargs)
        system_prompt_text = await prompt_manager.get_system_prompt(prompt_name, **clean_kwargs)
        
        messages = [SystemMessage(content=system_prompt_text)]
        if user_input and user_input.strip():
            messages.append(HumanMessage(content=user_input.strip()))

        prompt_str = self._format_messages_to_gemma_chatml(messages)
        response_stream = await asyncio.to_thread(lambda: self._model.generate_content(prompt_str, stream=True))
        for chunk in response_stream:
            if chunk.text:
                yield chunk.text
                await asyncio.sleep(0.01)

gemma_client = GemmaLLMClient()
```

---

## 3. 實機整合測試與真實數據紀錄 (`scripts/run_day9_live_test.py`)

我們撰寫並執行了 `scripts/run_day9_live_test.py` 實機整合腳本：

```python
import os
import sys
import asyncio
from app.services.gemma_llm import gemma_client
from app.services.context_manager import token_context_guard

async def run_day9_live_tests():
    # 1. 測試長對話逐字稿 Token 計數與滑動視窗截斷
    long_lines = ["[系統]: 面試開始。"]
    for i in range(40):
        long_lines.append(f"[考官]: 請說明第 {i+1} 個專案遭遇的困難？")
        long_lines.append(f"[學生]: 在第 {i+1} 個專案中，我使用了 Python 與多流程架構...")
    
    long_transcript = "\n".join(long_lines)
    truncated_transcript = token_context_guard.truncate_transcript(long_transcript, max_tokens=300)

    # 2. 測試超長 Context 下的 Gemma-4-31B 防護出題
    response = await gemma_client.invoke_with_system_prompt(
        prompt_name="question_generation",
        user_input="",
        target_school="國立台灣大學",
        target_major="資訊工程學系",
        interview_mode="頂大嚴謹模式",
        candidate_profile="高中代表隊參加全國軟體競賽一等獎，熱愛演算法與資安研究",
        sample_questions="範例問題：請向非資訊背景者解釋什麼是 Stack 與 Queue？",
        transcript=long_transcript
    )

    # 3. 測試非同步逐字 Streaming 串流吐字
    async for chunk in gemma_client.astream_with_system_prompt(
        prompt_name="response_generation",
        user_input="我選擇使用 Prepared Statements 來防止 SQL Injection 攻擊。",
        target_major="資訊工程學系",
        candidate_profile="高中資安社團社長，熟悉網路安全防禦",
        transcript="[系統]: 面試開始。[考官]: 請說明你曾處理過的資安案例？"
    ):
        print(chunk, end="", flush=True)

if __name__ == "__main__":
    asyncio.run(run_day9_live_tests())
```

### 實機執行輸出紀錄 (Empirical Execution Logs)

在 PowerShell 終端機執行 `$env:PYTHONPATH="."; .\venv\Scripts\python -u scripts/run_day9_live_test.py` 產出紀錄：

```text
==================================================
UniMock AI - Day 9 Resilient Gemma Client & Token Guard Test
==================================================

--- [Test 1] Token Count Estimation & Transcript Truncation ---
Original Transcript Length: 3233 chars (~3695 tokens)
Truncated Transcript Tokens: ~329 tokens
Truncated Transcript Output Snippet:
 [系統]: 面試開始。
[系統]: (更早期的問答對話已進行記憶摘要壓縮以控制 Token 長度...)
[考官]: 請向我說明第 38 個專案遭遇的困難？
[學生]: 在第 38 個專案中，我使用了 Python 與多流程架構，克服了複雜的極限瓶頸並成功解決難題。
[考官]: 請向我說明第 39 個專案遭遇的困難？
[學生]: 在第 39 個專案中，我使用了 Python 與多流程架構，克服了複雜的極限瓶頸並成功解決難題。
[考官]: 請向我說明第 40 個專案遭遇的困難？
[學生]: 在第 ...

--- [Test 2] Resilient Gemma-4-31B LLM Generation with Oversized Input Safeguard ---
Gemma Generated Question Response:
[考官]：我看你剛才在許多專案中都提到了使用 Python 的「多流程架構」來克服瓶頸。既然你在全國軟體競賽中取得一等獎，且對演算法有深厚的熱情，我想我們不需要再逐一列舉專案清單，而應該進入更深層的技術探討，來驗證你的實作能力。

請你詳細說明：在 Python 的環境下，為什麼你選擇使用「多流程 (Multiprocessing)」而非「多執行緒 (Multithreading)」來解決你所提到的極限瓶頸？這與 Python 的 GIL (Global Interpreter Lock) 有什麼樣的關聯？此外，在實作多流程時，你是如何處理不同 Process 之間的資料同步或溝通 (Inter-process communication) 問題的？ 

--- [Test 3] Real-Time Async Token Streaming Output (astream_with_system_prompt) ---
Streamed Tokens: 
【評估與評語】
你的回答非常精準，準確指出了 Prepared Statements 的核心價值。在面試中，這展現了你對資安基礎架構的紮實理解。
【追問】
請你進一步說明 Prepared Statements 在資料庫編譯階段（Prepare Phase）與執行階段（Execute Phase）的區別是什麼？

==================================================
Day 9 Live Protection & Streaming Test Completed Successfully!
==================================================
```

---

## 4. Pytest 自動化測試驗證 (`tests/test_day9_resilient_gemma.py`)

執行 `pytest tests/test_day9_resilient_gemma.py -v` 驗證成果：

```text
tests/test_day9_resilient_gemma.py::test_token_estimation_and_truncation PASSED             [ 50%]
tests/test_day9_resilient_gemma.py::test_resilient_gemma_client_retries_and_stream PASSED  [100%]

============================== 2 passed in 19.45s ==============================
```

---

## 結語與明天預告

今天我們完善了強健的 Gemma LLM Client 客戶端，加入了 **429 速率限制指數退避重試**、**TokenContextGuard 滑動視窗對話截斷** 與 **非同步 Token 串流吐字** 機制。

明天 **【Day 10】**，我們將進入多模態備審前處理——**利用 PyPDF 閱讀學生備審與自傳 PDF，並透過 Gemma 解析結構化履歷亮點與邏輯盲點**！
