# 【Day 6】面試知識庫建置：去識別化題庫清洗、Gemini Embedding 2 向量化與 Repository 模式實作

在完成了前端 UI 原型與動態參數設定後，今天我們邁入第二階段——**面試知識庫與向量庫建置**。我們將從原始題庫去識別化清洗開始，串接 Google AI Studio **Gemini Embedding 2** 模型，並實作統一的 **Repository 模式 (DB/Repo Layer)**，保護後端資料庫安全。

---

## 1. 資料來源、去識別化策略與 Gemini / Claude 清洗 Prompt 紀錄

### A. 資料庫來源與去識別化 (De-identification) 說明
本專案的原始面試題庫資料（位於 `datas/interview_questions_rows.csv`）是由**網路公開之各校系二階面試題庫資料**進行採集，結合**作者實戰面試經驗**進行修飾，並透過 **Gemini Chat** 與 **Claude Chat** 雙大語言模型進行深度資料清洗。

為了維護通用性與隱私安全，我們執行了 **「去識別化 (De-identification)」** 處理：
- **解除具體學校綁定：** 資料庫紀錄不綁定特定大專院校名稱（`school`），改為通用開放題目。
- **維護核心維度綁定：** 題庫精確綁定 **`department_group` (目標學群)**、**`department` (目標學系)**、**`question_category` (通用型問題 vs 技術專業型問題)** 以及 **`difficulty_level` (標準題 / 進階專業題 / 高難度申論題)**。

### B. Gemini / Claude 資料清洗 Prompt 紀錄

```markdown
> "請協助將採集的網路公開面試題庫與作者實戰面試經驗檔 `datas/interview_questions_rows.csv` 進行去識別化 ETL 資料清洗。
> 1. 去除所有具體學校名稱綁定，使題目具備通用開放性。
> 2. 為每一個題目提煉出精準欄位：`department_group` (學群)、`department` (學系)、`question_category` (通用型問題 / 技術專業型問題 / 情境申論型問題)、`difficulty_level` (標準題 / 進階專業題 / 高難度申論題)。
> 3. 針對題目補齊 STAR 架構引導語 `reference_answer` 與多維度 `rubric` 評分規準。
> 4. 輸出為格式嚴謹的 JSON 檔案 (`app/db/interview_questions_db.json`)。"
```

### C. 去識別化後 JSON DB 格式 Schema 規範 (`app/db/interview_questions_db.json`)

```json
[
  {
    "id": "q_0001",
    "deidentified": true,
    "department_group": "資訊電機學群",
    "department": "資訊工程學系",
    "question_category": "技術專業型問題",
    "difficulty_level": "進階專業題",
    "question": "請向非資訊背景的人解釋什麼是資料結構中的 Stack 與 Queue？",
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

### B. 編號追溯與增量自動跳過預處理腳本 (`scripts/incremental_preembed_questions.py`)

為了避免每次面試搜尋時動態對 2000+ 筆題目發起數千次 Gemini API 請求，並因應未來**不斷擴充 JSON 題庫**的需求，我們設計了具備 **編號追溯 (ID Traceability)** 與 **增量自動跳過 (Auto-Skip Existing)** 機制的預處理腳本：

1. **唯一 ID 追溯：** 每一筆題庫資料皆保留 `id` 欄位（如 `q_0001`、`q_0002`），在預處理前後皆能精確對照查找。
2. **自動跳過已轉過之題目：** 腳本會自動檢測 `q.get("embedding")` 是否已存在。若已計算過則自動跳過（`[SKIP q_0001]`），不消耗任何 API Token；僅針對新增或未向量化之題目發起 Gemini 請求。
3. **無縫資料擴充：** 未來任何時候新增題目進 `interview_questions_db.json` 後，直接執行該腳本即可完成增量向量擴充。

```python
import argparse
import json
import os
import sys
from app.services.embedding_service import embedding_service

def incremental_preembed(db_filepath: str, start_idx: int = 0, end_idx: int = None, force_reembed: bool = False):
    """
    Incremental Vector Pre-embedding Engine for UniMock AI.
    - Unique Question IDs (e.g., q_0001) for clear traceability.
    - Automatically detects and SKIPS questions that already have calculated embeddings.
    - Enables seamless data expansion when new questions are appended to JSON DB.
    """
    if not os.path.exists(db_filepath):
        return

    with open(db_filepath, "r", encoding="utf-8") as f:
        questions = json.load(f)

    total_count = len(questions)
    actual_end = total_count if end_idx is None or end_idx > total_count else end_idx

    skipped_count = 0
    updated_count = 0

    for i in range(start_idx, actual_end):
        q_item = questions[i]
        q_id = q_item.get("id", f"q_{i+1:04d}")
        q_text = q_item.get("question", "")
        existing_vec = q_item.get("embedding")

        # Skip logic: If embedding already exists and force_reembed is False
        if existing_vec and isinstance(existing_vec, list) and len(existing_vec) > 0 and not force_reembed:
            skipped_count += 1
            continue

        # Compute embedding for missing item
        vec = embedding_service.embed_query(q_text)
        q_item["embedding"] = vec
        updated_count += 1

    if updated_count > 0:
        with open(db_filepath, "w", encoding="utf-8") as f:
            json.dump(questions, f, ensure_ascii=False, indent=2)

    print(f"Incremental Pre-embedding Summary: Examined {actual_end - start_idx}, Skipped {skipped_count}, Newly Computed {updated_count}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Incremental Vector Pre-embedding Script")
    parser.add_argument("--start", type=int, default=0, help="Start index")
    parser.add_argument("--end", type=int, default=None, help="End index")
    parser.add_argument("--force", action="store_true", help="Force re-embed")
    args = parser.parse_args()

    db_path = os.path.join(os.path.dirname(__file__), "..", "app", "db", "interview_questions_db.json")
    incremental_preembed(db_path, start_idx=args.start, end_idx=args.end, force_reembed=args.force)
```

### C. 分批與增量執行指令範例

在 `unimock-ai/` 目錄下可以直接執行：

```bash
# 增量執行（自動跳過已轉過之題目，僅計算未轉換者）：
python scripts/incremental_preembed_questions.py

# 指定分批範圍（如 1 ~ 1000 筆）：
python scripts/batch_preembed_questions.py --start 0 --end 1000
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
    De-identified Unified Question Repository.
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
        department_group: Optional[str] = None,
        department: Optional[str] = None,
        question_category: Optional[str] = None,
        difficulty_level: Optional[str] = None,
        limit: int = 5
    ) -> List[Dict[str, Any]]:
        """Safe repository query function matching de-identified parameters."""
        matched = []
        for q in self._questions:
            if department and department not in q.get("department", ""):
                continue
            if department_group and department_group not in q.get("department_group", ""):
                continue
            if question_category and q.get("question_category") != question_category:
                continue
            if difficulty_level and q.get("difficulty_level") != difficulty_level:
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

### A. 去識別化清洗腳本執行
執行 `python scripts/clean_and_convert_db.py` 產出成果：
```text
Reading raw dataset for de-identification from: datas/interview_questions_rows.csv
Successfully de-identified and saved 2045 items to: app/db/interview_questions_db.json
```

### B. Pytest 自動化測試套件驗證
執行 `$env:PYTHONPATH="."; .\venv\Scripts\python -m pytest tests/test_repository.py`：
```text
tests/test_repository.py .... [100%]
4 passed in 4.88s
```
證實去識別化 Repository Function 運作無誤，完美達成資料庫安全隔離與彈性檢索！

---

## 結語與明天預告

今天我們順利完成題庫去識別化清洗、Gemini Embedding 2 向量化整合與 Repository 安全儲存庫模式實作。

明天 **【Day 7】**，我們將進行 **LangChain 環境配置與 Gemma-4-31B 模型 ChatML 提示樣板客製化串接**！
