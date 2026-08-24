# 【Day 22】極速響應：實作 SSE (Server-Sent Events) 流式文字串流傳輸

為了縮短使用者等待 AI 面試官輸出的首字延遲（TTFT），今天我們要實作 **SSE (Server-Sent Events)** 串流傳輸打字機效果。

---

## 1. 後端 SSE 端點實作 (`app/routers/interview_router.py`)

```python
from fastapi import APIRouter
from fastapi.responses import StreamingResponse
import asyncio

router = APIRouter(prefix="/api/v1/interview", tags=["Stream"])

async def mock_stream_generator(text: str):
    words = text.split(" ")
    for word in words:
        yield f"data: {word} \n\n"
        await asyncio.sleep(0.08)

@router.get("/stream-response")
async def stream_response(prompt: str):
    response_text = "請詳細說明你在處理此技術問題時的具體步驟？"
    return StreamingResponse(mock_stream_generator(response_text), media_type="text/event-stream")
```

---

## 2. 前端 EventSource 事件接收 (`frontend/stream.js`)

```javascript
function listenToInterviewStream(promptText) {
  const outputBox = document.getElementById('ai-question-box');
  outputBox.innerText = '';

  const eventSource = new EventSource(`/api/v1/interview/stream-response?prompt=${encodeURIComponent(promptText)}`);
  
  eventSource.onmessage = (event) => {
    outputBox.innerText += event.data;
  };

  eventSource.onerror = () => {
    eventSource.close();
  };
}
```

---

## 結語與明天預告

今天我們實現了 SSE 串流打字機渲染，大大提升了對話響應速度。

明天 **【Day 23】**，我們將整合 Web Speech API，讓學生可以用麥克風直接口語答題！
