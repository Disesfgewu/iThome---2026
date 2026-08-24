# 【Day 14】LangChain Memory 實戰：多輪對話記憶與上下文滑動視窗

多輪面試中，模型必須記住前幾輪學生的回答與提問脈絡。今天我們要使用 LangChain 的 **`ConversationTokenBufferMemory`** 實作動態滑動視窗記憶。

---

## 1. 對話記憶管理機制

為了避免長文本對話超過 Gemma-4-31B-it 的 Token 限制並導致推論延遲過長，我們保留全域 Session 歷史，但送給模型時限制最大 Token 數（例如 2048 Tokens）。

---

## 2. 記憶模組實作 (`app/services/memory_manager.py`)

```python
from langchain.memory import ConversationTokenBufferMemory
from app.services.gemma_llm import get_gemma_model

class SessionMemoryManager:
    def __init__(self):
        self.memories = {}
        self.llm = get_gemma_model()

    def get_memory(self, session_id: str):
        if session_id not in self.memories:
            self.memories[session_id] = ConversationTokenBufferMemory(
                llm=self.llm,
                max_token_limit=2048,
                return_messages=True
            )
        return self.memories[session_id]

    def add_turn(self, session_id: str, user_input: str, ai_response: str):
        mem = self.get_memory(session_id)
        mem.save_context({"input": user_input}, {"output": ai_response})
```

---

## 結語與明天預告

今天我們打通了多輪對話記憶與 Token 視窗控管。

明天 **【Day 15】**，我們將進入評測大腦設計，基於 STAR 原則構建多維度評分矩陣！
