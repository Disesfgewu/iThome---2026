# 【Day 19】後端 API 端點大整合：串接 Session、對話鏈與評分管線

今天我們要將前面實作的 PDF 備審解析、對話狀態機、Gemma 模型與評測大腦完整串接起來，構建四個核心 FastAPI RESTful 路由端點。

---

## 1. 核心四端點架構

- **`POST /api/v1/profile/upload-resume`**: 接收 PDF 上傳並產出 `CandidateProfile`。
- **`POST /api/v1/interview/start`**: 初始面試狀態並輸出第一道破冰題。
- **`POST /api/v1/interview/respond`**: 提交學生回答並由 Agent 動態深挖或推進下一題。
- **`GET /api/v1/interview/{session_id}/report`**: 匯聚對話紀錄生成結構化 `EvaluationReport`。

---

## 2. API 路由入口整合程式碼 (`app/main.py`)

```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import profile_router, interview_router

app = FastAPI(
    title="UniMock AI Engine",
    description="基於 Gemma-4-31B-it 的智慧升學模擬面試系統",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(profile_router.router)
app.include_router(interview_router.router)
```

---

## 結語與明天預告

今天我們完成了後端 API 系統的大串接。

明天 **【Day 20】**，我們將使用 Pytest 執行完整後端自動化測試與端到端驗收！
