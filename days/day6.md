# 【Day 6】面試知識庫建置：題庫清洗、Gemini Embedding 2 向量化與 Repository 模式實作

在完成了前端 UI 原型與動態參數設定後，今天我們邁入第二階段——**面試知識庫與向量庫建置**。我們將從原始題庫清洗開始，串接 Google AI Studio **Gemini Embedding 2** 模型，並實作統一的 **Repository 模式 (DB/Repo Layer)**，保護後端資料庫安全。

---

## 1. 資料來源與 Gemini / Claude 清洗 Prompt 紀錄

### A. 資料庫來源說明
本專案的原始面試題庫資料（位於 `datas/interview_questions_rows.csv`）是由**網路公開之各校系二階面試題庫資料**進行採集，結合**作者多年輔導備審與實戰面試經驗**進行修飾，並透過 **Gemini Chat** 與 **Claude Chat** 雙大語言模型進行深度資料清洗、語意標籤與評分規準 (Rubric) 的增強調校。

### B. Gemini / Claude 資料清洗 Prompt 紀錄

```markdown
> "請協助將採集的網路公開面試題庫與作者實戰面試經驗檔 `datas/interview_questions_rows.csv` 進行 ETL 資料清洗。
> 1. 為每一個題目提煉出精準欄位：`school` (學校)、`department_group` (學群)、`department` (學系)、`question_type` (個人特質/選系動機/專業知識/情境題)、`school_tier` (頂尖國立/地區國立/私立名校)。
> 2. 針對題目補齊 STAR 架構引導語 `reference_answer` 與多維度 `rubric` 評分規準。
> 3. 輸出為格式嚴謹的 JSON 檔案 (`app/db/interview_questions_db.json`)。"
```

### C. 轉換後 JSON DB 格式 Schema 規範 (`app/db/interview_questions_db.json`)

```json
[
  {
    "id": "q_0001",
    "school": "國立臺灣大學",
    "department_group": "資訊電機學群",
    "department": "資訊工程學系",
    "question_type": "專業知識",
    "question": "請向非資訊背景的人解釋什麼是資料結構中的 Stack 與 Queue？",
    "difficulty_mode": "頂尖名校模式",
    "school_tier": "頂尖國立",
    "dept_tags": ["資訊工程", "資料結構"],
    "reference_answer": "Stack 採用 LIFO (後進先出) 概念，如疊盤子；Queue 採用 FIFO (先進先出) 概念，如排隊買票...",
    "rubric": {
      "logic_structure": "評估是否採用 STAR 原則或比喻清晰度",
      "major_relevance": "評估專業術語與學系契合度",
      "communication_clarity": "評估口條流暢度與語速",
      "adaptability": "評估面對追問的應變韌性"
    }
  }
]
```

---

## 2. Gemini Embedding 2 向量化整合 (`app/services/embedding_service.py`)

為了支援高精度的面試題目語意相似度檢索，我們採用 Google AI Studio 託管的旗艦 Embedding 模型 **Gemini Embedding 2** (`models/text-embedding-004`)。

### A. Embedding 配置 Prompt & 程式碼範例

```python
import os
import math
from typing import List
import google.generativeai as genai
from app.config import settings

class GeminiEmbeddingService:
    """
    Google AI Studio Gemini Embedding 2 (text-embedding-004) Model Wrapper.
    """
    def __init__(self, model_name: str = "models/text-embedding-004"):
        self.model_name = model_name
        self.api_key = settings.GEMINI_API_KEY or os.environ.get("GEMINI_API_KEY", "")
        if self.api_key:
            genai.configure(api_key=self.api_key)

    def embed_query(self, text: str) -> List[float]:
        """Generate 768-dimensional normalized embedding vector for query."""
        if not text or not text.strip():
            return [0.0] * 768

        if self.api_key:
            try:
                result = genai.embed_content(
                    model=self.model_name,
                    content=text,
                    task_type="retrieval_query"
                )
                embedding = result.get("embedding", [])
                if embedding:
                    return self._normalize(embedding)
            except Exception as e:
                print(f"[GeminiEmbeddingService] API Warning: {e}. Fallback to pseudo-vector.")

        return self._pseudo_embedding(text)

    def _normalize(self, vec: List[float]) -> List[float]:
        norm = math.sqrt(sum(x * x for x in vec))
        return [x / norm for x in vec] if norm > 0 else vec

embedding_service = GeminiEmbeddingService()
```

---

## 3. 統一 DB / Repository 安全防護層實作 (`app/repositories/question_repository.py`)

為了維護後端資料安全，避免商業邏輯端點（Router）直接操作或竄改 JSON 資料庫，我們採用 **Repository Pattern (儲存庫模式)** 建構隔離層。後端僅能調用安全封裝的 Repo Functions：

```python
import json
import os
from typing import List, Dict, Any, Optional
from app.services.embedding_service import embedding_service

class QuestionRepository:
    """
    Unified Safe Question Repository.
    Encapsulates raw DB read/write and vector similarity search.
    """
    def __init__(self, db_path: Optional[str] = None):
        if db_path is None:
            db_path = os.path.join(os.path.dirname(__file__), "..", "db", "interview_questions_db.json")
        self.db_path = os.path.abspath(db_path)
        self._questions: List[Dict[str, Any]] = []
        self.load_database()

    def load_database(self) -> None:
        if os.path.exists(self.db_path):
            with open(self.db_path, "r", encoding="utf-8") as f:
                self._questions = json.load(f)

    def get_questions_by_filter(
        self,
        school: Optional[str] = None,
        department_group: Optional[str] = None,
        department: Optional[str] = None,
        question_type: Optional[str] = None,
        limit: int = 5
    ) -> List[Dict[str, Any]]:
        """Safe repository query function for interview engines."""
        matched = []
        for q in self._questions:
            if department and department not in q.get("department", ""):
                continue
            if department_group and department_group not in q.get("department_group", ""):
                continue
            if question_type and q.get("question_type") != question_type:
                continue
            matched.append(dict(q))
            if len(matched) >= limit:
                break
        return matched or [dict(q) for q in self._questions[:limit]]

    def search_similar_questions(self, query_text: str, top_k: int = 3) -> List[Dict[str, Any]]:
        """Vector similarity search using Gemini Embedding 2."""
        query_vec = embedding_service.embed_query(query_text)
        scored = []
        for q in self._questions:
            doc_vec = embedding_service.embed_query(q.get("question", ""))
            score = sum(a * b for a, b in zip(query_vec, doc_vec))
            scored.append((score, dict(q)))
        scored.sort(key=lambda x: x[0], reverse=True)
        return [q for score, q in scored[:top_k]]

question_repository = QuestionRepository()
```

---

## 4. 自動化清洗與 Repository 驗證結果

### A. 自動化清洗腳本執行
執行 `python scripts/clean_and_convert_db.py` 產出成果：
```text
Reading raw dataset from: datas/interview_questions_rows.csv
Successfully cleaned and saved 2045 high-quality questions to: app/db/interview_questions_db.json
```

### B. Pytest 自動化測試套件驗證
執行 `pytest tests/test_repository.py`：
```text
tests/test_repository.py .... [100%]
4 passed in 5.21s
```
證實 Repository Function 運作無誤，完美達成資料庫安全隔離防護！

---

## 結語與明天預告

今天我們順利完成 2045 筆題庫清洗、Gemini Embedding 2 向量化整合與 Repository 安全儲存庫模式實作。

明天 **【Day 7】**，我們將進行 **LangChain 環境配置與 Gemma-4-31B 模型 ChatML 提示樣板客製化串接**！
