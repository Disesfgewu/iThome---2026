# 【Day 9】模組化大腦：LLM 後端 Client 穩定度、429 重試與對話上下文管理模組封裝

在完成了 Day 7 的 Gemma 4 LLM 客戶端與 Day 8 的 RAG 全方位履歷檢索器後，今天我們進入 AI 大腦的關鍵防禦層搭建——**LLM Client 穩定度強化、429 Rate Limit 指數退避重試（Exponential Backoff）、Token 計數器與滑動視窗對話上下文管理 (TokenContextGuard)，以及非同步串流輸出 (Async Streaming)**。

---

## 1. 使用者提示詞 (User Prompt) 與關鍵防禦需求

> 💬 **User Prompt**：
> 「由於 LLM 或有 429 和 too many tokens input 之類的問題 我們需要強化封裝這個 client 物件去進行保護操作 請你根據 Day9 的計劃設計進行開發 開發完後 並一樣 紀錄成果和我給你的 Prompt 到對應的 MD 中」

根據這項關鍵需求，我們實現了四大關鍵防禦機制：
1. **`TokenContextGuard`**：Token 計數與滑動視窗對話動態截斷（防止 Context Window Overflow）。
2. **`GemmaLLMClient` 429 重試迴圈**：429 Rate Limit 與網路錯情指數退避重試。
3. **`astream_with_system_prompt`**：非同步 Token 串流吐字。

---

## 2. 核心機制實作程式碼片段

### A. 滑動視窗對話上下文管理器 (`TokenContextGuard`)
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

### B. 429 重試與非同步串流 (`GemmaLLMClient`)
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

## 3. 測試 Demo 與實機輸出紀錄 (Live Execution Demo & Output Logs)

執行 `scripts/run_day9_live_test.py` 實機測試關鍵結果：

- **長對話 Token 截斷紀錄**：
  原始對話長度 3,233 字（約 3,695 tokens）成功經由滑動視窗精準截斷至 **329 tokens**！
  ```text
  [系統]: 面試開始。
  [系統]: (更早期的問答對話已進行記憶摘要壓縮以控制 Token 長度...)
  [考官]: 請向我說明第 38 個專案遭遇的困難？
  [學生]: 在第 38 個專案中，我使用了 Python 與多流程架構...
  ```
- **Gemma-4-31B 機敏回應輸出**：
  考官偵測到對話中的重複回答模式，主動打破循環並深挖技術核心：
  > *「[考官]：我看你剛才在許多專案中都提到了使用 Python 的『多流程架構』來克服瓶頸。既然你在全國軟體競賽中取得一等獎，且對演算法有深厚的熱情，我想我們不需要再逐一列舉專案清單，而應該進入更深層的技術探討。請你詳細說明：在 Python 的環境下，為什麼你選擇使用『多流程 (Multiprocessing)』而非『多執行緒 (Multithreading)』？這與 Python 的 GIL (Global Interpreter Lock) 有什麼關聯？」*
- **非同步 Token 串流吐字**：`astream_with_system_prompt` 成功完成逐字即時吐字傳輸。

---

## 4. Pytest 自動化測試驗證數據

```text
tests/test_day9_resilient_gemma.py::test_token_estimation_and_truncation PASSED [ 50%]
tests/test_day9_resilient_gemma.py::test_resilient_gemma_client_retries_and_stream PASSED [100%]

======================= 2 passed in 54.67s =======================
```

---

## 結語與明天預告

今天我們完成了 Gemma LLM Client 客戶端的 **429 指數退避重試**、**TokenContextGuard 滑動視窗動態截斷** 與 **非同步 Token 串流**。

明天 **【Day 10】**，我們將進入多模態備審前處理——**利用 PyPDF 閱讀學生備審與自傳 PDF，並透過 Gemma 解析結構化履歷亮點與邏輯盲點**！
