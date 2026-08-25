# 【Day 9】模組化大腦：LLM 後端 Client 穩定度、429 重試與對話上下文管理模組封裝

在完成了 Day 7 的 Gemma 4 LLM 客戶端與 Day 8 的 RAG 全方位履歷檢索器後，今天我們進入 AI 大腦的關鍵防禦層搭建——**LLM Client 穩定度強化、429 Rate Limit 指數退避重試（Exponential Backoff）、Token 計數器與滑動視窗對話上下文管理 (TokenContextGuard)，以及非同步串流輸出 (Async Streaming)**。

---

## 1. 核心機制一：滑動視窗對話上下文管理器 (`TokenContextGuard`)

為防止學生與考官過往問答逐字稿 (`transcript`) 累積過長導致 LLM 上下文爆表 (Context Window Overflow / Too Many Tokens Input)，我們設計了 **`TokenContextGuard`** 機制：
- **Token 動態估算**：針對中英文混合文本（繁簡中文約 1.5 字符/Token）即時計算長度。
- **滑動視窗動態截斷**：保留系統標頭與最近的焦點對話，對更早期的歷史問答插入記憶壓縮摘要。

```python
class TokenContextGuard:
    def estimate_tokens(self, text: str) -> int:
        """估算繁簡中文與英文混合文本之 Token 長度"""
        cjk_count = len(re.findall(r'[\u4e00-\u9fff]', text))
        non_cjk_words = len(re.findall(r'\b\w+\b', text))
        return int(cjk_count * 1.5 + non_cjk_words * 1.3)

    def truncate_transcript(self, transcript: str, max_tokens: int = 3000) -> str:
        """滑動視窗動態截斷早期問答對話"""
        if self.estimate_tokens(transcript) <= max_tokens:
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
```

---

## 2. 核心機制二：429 重試與非同步串流 (`GemmaLLMClient`)

針對高併發或免費層 API 限制時常見的 `429 Rate Limit / ResourceExhausted` 錯誤，我們在 `GemmaLLMClient` 中封裝了**指數退避重試迴圈 (Exponential Backoff Loop)**，並提供 `astream_with_system_prompt` 作為前端 SSE 串流輸出的核心方法：

```python
class GemmaLLMClient(BaseChatModel):
    max_retries: int = 3
    base_backoff_delay: float = 2.0

    def _generate(self, messages: List[BaseMessage], **kwargs: Any) -> ChatResult:
        """指數退避自動重試迴圈，防禦 429 限流與網路暫態錯誤"""
        prompt_str = self._format_messages_to_gemma_chatml(messages)

        last_exception = None
        for attempt in range(self.max_retries):
            try:
                response = self._model.generate_content(prompt_str)
                clean_text = re.sub(r"<end_of_turn>$", "", response.text).strip()
                return ChatResult(generations=[ChatGeneration(message=AIMessage(content=clean_text))])
            except Exception as e:
                last_exception = e
                err_msg = str(e).lower()
                if "429" in err_msg or "resource_exhausted" in err_msg:
                    time.sleep(self.base_backoff_delay * (2 ** attempt) + 1.0)
                else:
                    time.sleep(self.base_backoff_delay * (attempt + 1))

        raise RuntimeError(f"Gemma LLM 呼叫失敗，已重試 {self.max_retries} 次: {last_exception}")

    async def astream_with_system_prompt(self, prompt_name: str, user_input: str = "", **prompt_kwargs) -> AsyncGenerator[str, None]:
        """非同步 Token 串流輸出，為前端 SSE 串流吐字提供基礎"""
        clean_kwargs = token_context_guard.sanitize_prompt_kwargs(prompt_kwargs)
        system_prompt_text = await prompt_manager.get_system_prompt(prompt_name, **clean_kwargs)
        prompt_str = self._format_messages_to_gemma_chatml([SystemMessage(content=system_prompt_text)])
        
        response_stream = await asyncio.to_thread(lambda: self._model.generate_content(prompt_str, stream=True))
        for chunk in response_stream:
            if chunk.text:
                yield chunk.text
                await asyncio.sleep(0.01)
```

---

## 3. 實機測試數據紀錄

執行 `scripts/run_day9_live_test.py` 實機測試關鍵結果：

- **長對話 Token 截斷**：長達 40 輪對話（3,233 字，約 3,695 tokens）成功經由滑動視窗精準截斷至 **329 tokens**，成功防止爆表。
- **Gemma-4-31B 機敏回應**：考官偵測到對話中的重複回答模式，主動打破循環並深挖技術核心：
  > *「[考官]：我看你剛才在許多專案中都提到了使用 Python 的『多流程架構』來克服瓶頸... 請你詳細說明：在 Python 的環境下，為什麼你選擇使用『多流程 (Multiprocessing)』而非『多執行緒 (Multithreading)』？這與 Python 的 GIL (Global Interpreter Lock) 有什麼關聯？」*
- **非同步 Token 串流吐字**：`astream_with_system_prompt` 成功完成逐字即時吐字傳輸。

---

## 4. Pytest 單元測試結果

```text
tests/test_day9_resilient_gemma.py::test_token_estimation_and_truncation PASSED [ 50%]
tests/test_day9_resilient_gemma.py::test_resilient_gemma_client_retries_and_stream PASSED [100%]

======================= 2 passed in 54.67s =======================
```

---

## 結語與明天預告

今天我們以精簡強健的模組完成了 Gemma LLM Client 客戶端的 **429 指數退避重試**、**TokenContextGuard 滑動視窗動態截斷** 與 **非同步 Token 串流**。

明天 **【Day 10】**，我們將進入多模態備審前處理——**利用 PyPDF 閱讀學生備審與自傳 PDF，並透過 Gemma 解析結構化履歷亮點與邏輯盲點**！
