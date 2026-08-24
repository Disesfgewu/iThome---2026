# UniMock AI 🎓

UniMock AI 是一個基於 Gemma-4-31B-it 與 LangChain 打造的智慧升學模擬面試 Agent 系統。

## 專案結構 (Directory Structure)

```text
unimock-ai/
├── app/
│   ├── __init__.py
│   ├── main.py                  # FastAPI 入口點
│   ├── config.py                # 環境變數與設定載入
│   ├── schemas/                 # Pydantic 資料模型
│   │   ├── __init__.py
│   │   ├── profile.py
│   │   ├── interview.py
│   │   └── report.py
│   ├── services/                # 業務邏輯與 LLM 封裝
│   │   ├── __init__.py
│   │   ├── gemma_client.py      # Google AI Studio / Gemma 客戶端
│   │   ├── document_parser.py   # PDF 解析模組
│   │   ├── interview_agent.py   # LangChain 面試對話狀態機
│   │   └── evaluator.py         # 評分與診斷生成器
│   └── routers/                 # API 路由
│       ├── __init__.py
│       ├── profile_router.py
│       └── interview_router.py
├── tests/                       # 單元測試
├── .env.example                 # 環境變數範本
├── requirements.txt             # Python 相依清單
└── README.md
```

## 快速啟動 (Quick Start)

### 1. 建立並啟動 Python 虛擬環境

```bash
python -m venv venv
# Windows:
.\venv\Scripts\activate
# Linux/macOS:
source venv/bin/activate
```

### 2. 安裝相依套件

```bash
pip install -r requirements.txt
```

### 3. 設定環境變數

```bash
cp .env.example .env
```

### 4. 啟動 FastAPI 服務

```bash
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

訪問 `http://127.0.0.1:8000/docs` 可查看自動生成的 Swagger UI API 文件。

### 5. 執行單元測試

```bash
pytest
```
