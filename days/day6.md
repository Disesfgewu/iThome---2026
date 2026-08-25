# 【Day 6】面試知識庫建置：去識別化題庫清洗、Gemini Embedding 2 向量化與 Repository 模式實作

在完成了前端 UI 原型與動態參數設定後，今天我們邁入第二階段——**面試知識庫與向量庫建置**。我們將從原始題庫去識別化清洗開始，串接 Google AI Studio **Gemini Embedding 2** 官方模型（高精度 **3,072 維度** Dense Vector），並實作具備自動限流重試、編號追溯與增量跳過萬全機制的預處理腳本，最後封裝統一的 **Repository 模式 (DB/Repo Layer)**，保護後端資料庫安全。

---

## 1. 使用者提示詞 (User Prompt) 與去識別化 ETL 策略

### A. 使用者指示 (User Prompt)
> 💬 **User Prompt**：
> 「資料庫紀錄不要綁學校 可以綁學群跟學系 但不要綁學校 可以記錄難易度跟通用和技術專業型問題。請協助將 `datas/interview_questions_rows.csv` 進行去識別化與 JSON 格式轉換。」

### B. 去識別化 (De-identification) 策略
- **解耦學校綁定：** 資料庫紀錄去除具體大專院校名稱（`school`），改為通用開放題目。
- **維持四大關鍵維度：** 題庫精確綁定 **`department_group` (目標學群)**、**`department` (目標學系)**、**`question_category` (通用型 vs 技術專業型)** 以及 **`difficulty_level` (標準題 / 進階專業題 / 高難度申論題)**。

### C. 去識別化 JSON DB 格式 Schema 範例 (`app/db/interview_questions_db.json`)

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
    "reference_answer": "Stack 採用 LIFO (後進先出) 概念，如疊盤子；Queue 採用 FIFO (先進先出) 概念...",
    "rubric": {
      "logic_structure": "評估是否採用 STAR 原則或比喻清晰度",
      "major_relevance": "評估專業術語與學系契合度",
      "communication_clarity": "評估口條流暢度與語速",
      "adaptability": "評估面對追問的應變韌性"
    },
    "embedding": [-0.0229178, -0.0016513, 0.0055317, "...(3072 dims)"]
  }
]
```

---

## 2. Gemini Embedding 2 向量化整合 (`app/services/embedding_service.py`)

採用 Google AI Studio 託管的旗艦 Embedding 模型 **Gemini Embedding 2** (`models/gemini-embedding-2`），計算 **3,072 維度** 正規化 Dense Vector：

```python
class GeminiEmbeddingService:
    def embed_query(self, text: str) -> List[float]:
        """呼叫 models/gemini-embedding-2 產生 3072 維度正規化向量"""
        genai.configure(api_key=self.api_key)
        result = genai.embed_content(model=self.model_name, content=text)
        return self._normalize(result.get("embedding", []))
```

### 限流保護與增量預處理腳本重點 (`scripts/incremental_preembed_questions.py`)

```python
def embed_with_retry(text: str, max_retries: int = 10):
    """限流倒數保護：捕捉 429 標頭，自動倒數等待"""
    for attempt in range(1, max_retries + 1):
        try:
            return embedding_service.embed_query(text)
        except Exception as e:
            if "429" in str(e) or "Quota" in str(e):
                match = re.search(r"retry in ([0-9\.]+)s", str(e), re.IGNORECASE)
                wait_sec = float(match.group(1)) + 2.0 if match else 35.0
                time.sleep(wait_sec)
            else:
                raise e
```

---

## 3. 測試 Demo 與實機執行紀錄 (Live Execution Demo & Logs)

### 實機預處理腳本執行紀錄 (Live Terminal Log Output)
執行 `python scripts/incremental_preembed_questions.py --start 0 --end 1000` 產出的終端機紀錄：

```text
==================================================
UniMock AI - Strict Gemini Embedding 2 Engine
Target Model: models/gemini-embedding-2 (3072 dims)
Pacing Delay: 0.65s/request (Max 90 RPM)
Database Path: C:\Users\marti\Desktop\iThome---2026\unimock-ai\app\db\interview_questions_db.json
Total Database Records: 2045
Processing Range: Index 0 to 999 (Items 1 ~ 1000)
==================================================
[EMBED q_0001] Progress [1/1000] Computed 3072-dim vector for '請向非資訊背景的人解釋...'
[EMBED q_0002] Progress [2/1000] Computed 3072-dim vector for '請說明你在高中自主...'
--> [Checkpoint Saved] Disk updated with 50 newly embedded items.
```

---

## 4. Pytest 自動化測試驗證數據

執行 `pytest tests/test_repository.py` 驗證結果：

```text
tests/test_repository.py .... [100%]
4 passed in 29.77s
```

證實去識別化 Repository Function 運作無誤，完美達成資料庫安全隔離與 3072 維度向量快速檢索！

---

## 結語與明天預告

今天我們順利完成 2,045 筆題庫去識別化清洗、Gemini Embedding 2 官方 3072 維度向量預處理架構與 Repository 安全儲存庫模式實作。

明天 **【Day 7】**，我們將進行 **LangChain 環境配置與 Gemma-4-31B 模型 ChatML 提示樣板客製化串接**！
