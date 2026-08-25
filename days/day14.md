# 【Day 14】LangChain Memory 實戰：多輪對話記憶與上下文滑動視窗

在多輪面試過程中，AI 面試官必須精準記住前幾輪學生的回答與發問脈絡。今天我們採用 LangChain 訊息抽象與滑動 Token 視窗（Sliding Token Buffer Window Memory）技術，實作正式的**多輪對話記憶管理器 (`LangChainMemoryManager`)**。

---

## 1. 使用者提示詞 (User Prompt) 與多輪記憶需求

> 💬 **User Prompt**：
> 「多輪面試中，模型必須記住前幾輪學生的回答與提問脈絡。今天我們要使用 LangChain 的 Conversation Token Memory 實作動態滑動視窗記憶，在不超過 Gemma 4 Token 限制的前題下，維持長期連貫的上下文對話體驗。」

---

## 2. LangChain 對話記憶架構 (LangChain Memory Architecture)

```mermaid
graph TD
    A["學生與考官進行 Ask/Answer 對話"] --> B["LangChainMemoryManager (HumanMessage / AIMessage)"]
    B --> C["即時追蹤對話 Message 鏈長度"]
    C -->|長度超過 Token 上限 (2048 Tokens)| D["自動觸發滑動視窗彈性修剪 (_trim_messages)"]
    C -->|長度合規| E["導出結構化對話上下文 Buffer String"]
    D --> E
    E --> F["注入 Gemma-4-31B 進行多輪連貫推論"]
```

---

## 3. 核心機制實作程式碼片段 (`app/services/memory_manager.py`)

```python
class LangChainMemoryManager:
    """LangChain 多輪對話記憶管理器，具備滑動 Token 視窗修剪機制"""
    def __init__(self, max_token_limit: int = 2048):
        self.max_token_limit = max_token_limit
        self._memories: Dict[str, List[BaseMessage]] = {}

    def get_or_create_messages(self, session_id: str) -> List[BaseMessage]:
        if session_id not in self._memories:
            self._memories[session_id] = []
        return self._memories[session_id]

    def add_user_message(self, session_id: str, message: str):
        msgs = self.get_or_create_messages(session_id)
        msgs.append(HumanMessage(content=message))
        self._trim_messages(session_id)

    def add_ai_message(self, session_id: str, message: str):
        msgs = self.get_or_create_messages(session_id)
        msgs.append(AIMessage(content=message))
        self._trim_messages(session_id)

    def _trim_messages(self, session_id: str):
        msgs = self.get_or_create_messages(session_id)
        max_chars = self.max_token_limit * 2
        while len(msgs) > 2 and sum(len(m.content) for m in msgs) > max_chars:
            msgs.pop(0)

    def get_buffer_string(self, session_id: str) -> str:
        msgs = self.get_or_create_messages(session_id)
        return "\n".join([f"{'[考官]' if isinstance(m, AIMessage) else '[學生]'}: {m.content}" for m in msgs])
```

### 整合至 FastAPI Session 路由 (`app/routers/interview.py`)

```python
@router.post("/setup", response_model=InterviewSetupResponse)
async def setup_interview_session(req: InterviewSetupRequest):
    session_id = session_repository.create_session(req.target_school, req.target_major, req.interview_mode, req.candidate_profile)
    rag_res = await rag_service.generate_rag_question_for_candidate(...)
    first_question = rag_res["generated_question"]

    # 初始化 LangChain Memory 並紀錄考官首題
    memory_manager.get_or_create_messages(session_id)
    memory_manager.add_ai_message(session_id, first_question)
    return InterviewSetupResponse(...)

@router.post("/answer", response_model=AnswerSubmitResponse)
async def submit_user_answer(req: AnswerSubmitRequest):
    session = session_repository.get_session(req.session_id)
    # 同步紀錄學生回答至 LangChain Memory
    memory_manager.add_user_message(req.session_id, req.user_answer)
    ...
    next_question = await gemma_client.invoke_with_system_prompt(...)
    # 同步紀錄考官追問至 LangChain Memory
    memory_manager.add_ai_message(req.session_id, next_question)
    return AnswerSubmitResponse(...)
```

---

## 4. 實機測試與真實 Terminal 輸出紀錄 (`scripts/run_day14_live_test.py`)

執行多輪記憶對話測試腳本，驗證 LangChain Memory 機制運作：

```text
==================================================
UniMock AI - Day 14 LangChain Memory Live Test
==================================================

--- [Step 1] Verifying LangChain ConversationTokenBufferMemory ---
Memory Buffer String:
[考官]: 你好，歡迎參加資工系模擬面試。
[學生]: 教授好，我主要研究演算法優化與系統開發。

--- [Step 2] Live FastAPI Session LangChain Memory Integration ---
Session Created: sess_d9d1547a71 | Memory Initialized.

Q2 Generated with Memory Context:
[考官]：（微微點頭，眼神溫和但帶著審視，語氣沉穩地回應）

很高興看到你對陽明交大資工系有這麼強烈的熱情，而且在高中階段就已經開始主動接觸競賽與專案實作，這展現了你的積極性。

不過，剛才你的回答比較偏向概括性的陳述。在面試中，我更希望看到你如何將「熱情」轉化為「具體的行動」與「解決問題的能力」。你提到的「專案優化」是一個很關鍵的詞，但在工程領域中，優化可能指的性能提升、程式碼精簡或是演算法的改進。

我想請你挑選一個你最引以為傲的專案或競賽經歷，詳細跟我分享：
1. 當時面臨的具體挑戰或問題是什麼？（Situation/Task）
2. 你採取了哪些具體的技術手段或步驟來進行「優化」？（Action）
3. 最後取得了什麼樣的量化結果或成效？（Result）

==================================================
Day 14 LangChain Memory Live Test Completed Successfully!
==================================================
```

---

## 結語與明天預告

今天我們完成了 **LangChain Memory 實戰：多輪對話記憶與上下文滑動視窗 (`LangChainMemoryManager`)**，確保系統能以彈性 Token 上限不斷維護流暢且連貫的上下文對話記憶。

明天 **【Day 15】**，我們將進入 **SSE 打字機流式吐字與前後端即時通訊 (Server-Sent Events & Real-time Streaming)**，讓 React 前端正式體驗即時打字機問答！
