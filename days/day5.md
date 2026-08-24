# 【Day 5】逆向工程：從 UI 分析資料流與後端 Pydantic 物件架構設計

在完成了前端 UI 原型與動態狀態切換後，今天我們要採用 **UI-Driven API Design（UI 驅動 API 設計）** 的逆向工程思維，從前端畫面的每一個展示欄位，推導出後端 Pydantic 資料契約（Data Contracts）。

---

## 1. 從 UI 元件推導 API Payload

| 前端 UI 區塊 | 需要的資料欄位 | 對應 Pydantic 模型 |
| --- | --- | --- |
| 上傳自傳區 | 檔案、目標申請學系 | `CandidateProfile` |
| 經歷與亮點卡片 | 專案分類、名稱、描述、幹部經歷、證照 | `HighlightItem`, `CandidateProfile` |
| 對話紀錄窗格 | 輪次索引、面試官發問、學生回答 | `DialogueTurn` |
| 雷達圖與診斷報告 | STAR 評分維度、逐題分析、改進建議 | `RubricScore`, `EvaluationReport` |

---

## 2. 核心 Pydantic Schemas 設計 (`app/schemas/`)

### `app/schemas/profile.py`
```python
from pydantic import BaseModel, Field
from typing import List, Optional

class HighlightItem(BaseModel):
    category: str = Field(description="專案實作 / 競賽獲獎 / 自主學習")
    title: str
    description: str

class CandidateProfile(BaseModel):
    target_major: str = Field(description="目標申請學系，如：資訊工程學系")
    background: Optional[str] = Field(default="", description="學生個人背景與簡介")
    leadership_experiences: List[str] = Field(default_factory=list, description="幹部與社團經歷")
    certificates: List[str] = Field(default_factory=list, description="證照與檢定紀錄")
    highlights: List[HighlightItem] = Field(default_factory=list, description="專案與特徵亮點")
    detected_blindspots: List[str] = Field(default_factory=list, description="自傳疑點與邏輯盲點")
```

### `app/schemas/interview.py`
```python
from pydantic import BaseModel, Field
from typing import Optional

class StartInterviewRequest(BaseModel):
    session_id: str
    target_major: str

class StartInterviewResponse(BaseModel):
    session_id: str
    first_question: str

class RespondInterviewRequest(BaseModel):
    session_id: str
    answer: str

class RespondInterviewResponse(BaseModel):
    session_id: str
    next_question: Optional[str] = None
    is_finished: bool = False
```

---

## 3. 前後端通訊 API 規格整理

```
[Client (UI)] ─── POST /api/v1/profile/upload-resume ──► [CandidateProfile]
[Client (UI)] ─── POST /api/v1/interview/start       ──► [StartInterviewResponse]
[Client (UI)] ─── POST /api/v1/interview/respond     ──► [RespondInterviewResponse]
[Client (UI)] ─── GET  /api/v1/interview/{id}/report ──► [EvaluationReport]
```

---

## 結語與明天預告

今天我們順利完成全端 Data Contracts 設計，第一階段「專案啟航與 UI 原型」圓滿落幕！

明天 **【Day 6】**，我們將邁入階段二：**開始建置面試題庫向量資料庫與 Embedding Pipeline**！
