# 【Day 6】面試知識庫建置：歷年面試題庫清理與向量 Embedding 實戰

邁入專案開發第二階段，今天我們要建置 **UniMock AI** 的面試題庫與專業資料庫（Vector Store），讓 AI 面試官在發問時能夠參考真實歷年面試考古題。

---

## 1. 面試題庫資料前處理 Pipeline

我們收集了資訊、商管、醫學等領域的歷年二階甄試考古題與專業題庫，結構如下：

```json
[
  {
    "major": "資訊工程學系",
    "category": "專案追問",
    "question": "請說明你在高中專案中遇到的最大技術挑戰與解決方案？"
  },
  {
    "major": "資訊工程學系",
    "category": "基礎概念",
    "question": "請向非資訊背景的人解釋什麼是資料結構中的 Stack 與 Queue？"
  }
]
```

---

## 2. 向量 Embedding 與 ChromaDB 建構腳本 (`app/services/vector_store.py`)

使用 LangChain 與本地 Embedding 模型建立向量資料庫：

```python
from langchain_community.document_loaders import JSONLoader
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings

class VectorStoreService:
    def __init__(self, persist_directory: str = "./data/chroma_db"):
        self.embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
        self.persist_directory = persist_directory

    def build_index(self, json_filepath: str):
        print(f"📖 正在載入題庫資料：{json_filepath}")
        # 載入並切分文字 Document
        # 建構本地 Chroma 向量資料庫
        print("✅ 向量資料庫建立完成！")

    def get_retriever(self):
        db = Chroma(persist_directory=self.persist_directory, embedding_function=self.embeddings)
        return db.as_retriever(search_kwargs={"k": 3})
```

---

## 結語與明天預告

今天我們完成了面試題庫資料的前處理與向量資料庫封裝。

明天 **【Day 7】**，我們將配置 LangChain 環境並客製化 Gemma-4-31B-it 的 ChatModel 封裝！
