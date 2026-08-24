# 【Day 9】模組化大腦：LLM 後端 Client 與對話上下文管理模組封裝

今天我們要為 LLM Client 打造強健的客製化封裝，提供指數退避（Exponential Backoff）重試、Token 計數與串流輸出能力。

---

## 1. 強健的 Gemma Client 封裝 (`app/services/gemma_client.py`)

```python
import time
from typing import Generator
from app.config import settings
import google.generativeai as genai

class ResilientGemmaClient:
    def __init__(self):
        genai.configure(api_key=settings.GEMINI_API_KEY)
        self.model = genai.GenerativeModel(settings.DEFAULT_MODEL_NAME)

    def generate_with_retry(self, prompt: str, max_retries: int = 3) -> str:
        for attempt in range(max_retries):
            try:
                response = self.model.generate_content(prompt)
                return response.text
            except Exception as e:
                print(f"⚠️ 請求失敗 (嘗試 {attempt + 1}/{max_retries}): {e}")
                time.sleep(2 ** attempt)
        raise RuntimeError("模型 API 呼叫超過最大重試次數")

    def generate_stream(self, prompt: str) -> Generator[str, None, None]:
        response = self.model.generate_content(prompt, stream=True)
        for chunk in response:
            if chunk.text:
                yield chunk.text
```

---

## 結語與明天預告

今天我們完善了後端 LLM Client 的穩定度與串流傳輸能力。

明天 **【Day 10】**，我們將整合 PDF 提取工具與 Gemma，實現學習歷程與自傳自動解析功能！
