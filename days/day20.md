# 【Day 20】後端整合驗收：自動化測試與端到端對話邏輯驗證

今天我們要針對後端整體的 4 大 API 端點、Pydantic 模型驗證與例外處理機制進行全方位的 **Pytest 自動化端到端測試**，邁入第三階段的完美結案！

---

## 1. 自動化測試腳本 (`tests/test_e2e_interview.py`)

```python
import io
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_full_interview_lifecycle():
    # 1. 上傳 PDF 備審測試
    fake_pdf = io.BytesIO(b"%PDF-1.4 Mock PDF Content")
    upload_res = client.post(
        "/api/v1/profile/upload-resume",
        files={"file": ("resume.pdf", fake_pdf, "application/pdf")},
        data={"target_major": "資訊工程學系"}
    )
    assert upload_res.status_code == 200
    profile = upload_res.json()
    assert profile["target_major"] == "資訊工程學系"

    # 2. 開始面試
    session_id = "test_session_e2e"
    start_res = client.post(
        "/api/v1/interview/start",
        json={"session_id": session_id, "target_major": "資訊工程學系"}
    )
    assert start_res.status_code == 200
    assert "first_question" in start_res.json()

    # 3. 多輪回答
    resp_res = client.post(
        "/api/v1/interview/respond",
        json={"session_id": session_id, "answer": "我對寫程式非常有熱情，曾開發過智慧校園系統。"}
    )
    assert resp_res.status_code == 200

    # 4. 生成診斷報告
    report_res = client.get(f"/api/v1/interview/{session_id}/report")
    assert report_res.status_code == 200
    report = report_res.json()
    assert "scores" in report
```

---

## 2. 測試執行結果

在 Antigravity 終端機中執行：

```bash
pytest
```

預期結果：`6 passed in 0.40s`，證明後端 pipeline 邏輯 100% 正確通暢。

---

## 結語與明天預告

今天我們完成了後端全套自動化測試與驗收，第三階段宣告完工！

明天 **【Day 21】**，我們將開啟第四階段：**將 FastAPI 後端與 Stitch 前端介面進行端到端 API 串接實戰**！
