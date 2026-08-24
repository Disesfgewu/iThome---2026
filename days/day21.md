# 【Day 21】前後端接軌：FastAPI 與 Stitch 生成前端的 API 串接實戰

第四階段正式開工！今天我們要將 **FastAPI** 後端服務與 **Stitch** 生成的前端 UI 進行 Fetch API 整合，實現 PDF 檔案上傳與即時問答對接。

---

## 1. 前端 API 呼叫模組 (`frontend/api.js`)

```javascript
const API_BASE = 'http://127.0.0.1:8000/api/v1';

// 1. 上傳 PDF 備審
async function uploadResume(file, targetMajor) {
  const formData = new FormData();
  formData.append('file', file);
  formData.append('target_major', targetMajor);

  const res = await fetch(`${API_BASE}/profile/upload-resume`, {
    method: 'POST',
    body: formData
  });
  return await res.json();
}

// 2. 啟動面試
async function startInterview(sessionId, targetMajor) {
  const res = await fetch(`${API_BASE}/interview/start`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ session_id: sessionId, target_major: targetMajor })
  });
  return await res.json();
}
```

---

## 2. 跨域 CORS 配置確認

確保後端 `app/main.py` 允許前端源：

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)
```

---

## 結語與明天預告

今天我們成功建立了前後端 HTTP RESTful API 通訊管道。

明天 **【Day 22】**，我們將實作 SSE (Server-Sent Events) 打字機串流，提升 AI 面試官的回應體感速度！
