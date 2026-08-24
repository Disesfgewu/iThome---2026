# 【Day 8】知識檢索：打造後端 RAG 檢索器與向量資料庫 API 服務

今天我們要實作 **RAG (Retrieval-Augmented Generation)** 檢索鏈，讓 AI 面試官在對話時能夠依據學生目標科系動態檢索考古題庫與評分標準。

---

## 1. RAG 檢索架構設計

```
[學生目標科系 + 回答] ──► [Similarity Search (ChromaDB)] ──► [Top-K 相關考古題]
                                                                  │
                                                                  ▼
[Gemma-4-31B-it] ◄── [System Prompt + 檢索脈絡 + 對話歷史] ◄──────┘
```

---

## 2. 檢索鏈服務實作 (`app/services/rag_service.py`)

```python
from app.services.vector_store import VectorStoreService
from app.services.gemma_llm import get_gemma_model
from langchain_core.runnables import RunnablePassthrough

class RAGSearchService:
    def __init__(self):
        self.vector_service = VectorStoreService()
        self.retriever = self.vector_service.get_retriever()
        self.llm = get_gemma_model()

    def query_interview_context(self, major: str, topic: str) -> str:
        docs = self.retriever.get_relevant_documents(f"{major} {topic}")
        return "\n".join([doc.page_content for doc in docs])
```

---

## 結語與明天預告

今天我們打通了向量檢索管道，成功將外掛知識庫引入面試 Agent。

明天 **【Day 9】**，我們將強化 LLM Client，加入 Token 計數、異常重試與流式傳輸（Streaming）機制！
