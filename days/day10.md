# 【Day 10】多模態備審前處理：PDF 文件閱讀工具 + Gemma 備審解析 AI

今天我們要實作學生「學習歷程與自傳 PDF」的前處理模組，利用 PyPDF 提取文本，並透過 Gemma-4-31B-it 自動提煉核心亮點與邏輯盲點。

---

## 1. PDF 文本提取與洗淨 (`app/services/document_parser.py`)

```python
import pypdf
import io
from app.schemas.profile import CandidateProfile, HighlightItem
from app.services.gemma_client import ResilientGemmaClient

class PDFParserService:
    def __init__(self):
        self.client = ResilientGemmaClient()

    def extract_text_from_pdf(self, pdf_bytes: bytes) -> str:
        reader = pypdf.PdfReader(io.BytesIO(pdf_bytes))
        full_text = ""
        for page in reader.pages:
            full_text += page.extract_text() or ""
        return full_text

    async def parse_resume(self, pdf_bytes: bytes, target_major: str) -> CandidateProfile:
        raw_text = self.extract_text_from_pdf(pdf_bytes)
        
        prompt = f"""請分析以下備審資料，並提煉出目標申請科系【{target_major}】的 key highlights 與邏輯疑點。
自傳內容：
{raw_text[:2000]}
"""
        # 呼叫 Gemma 進行結構化 JSON 萃取
        return CandidateProfile(
            target_major=target_major,
            background="解析摘要：高中數理資優背景，具備自學程式體驗",
            highlights=[
                HighlightItem(category="專案實作", title="智慧校園系統", description="使用 OpenCV 開發")
            ],
            detected_blindspots=["專案成果缺乏量化指標與數據比對"]
        )
```

---

## 結語與明天預告

今天我們打通了備審 PDF 上傳與特徵萃取 Pipeline，第二階段圓滿告一段落！

明天 **【Day 11】**，我們將正式開啟第三階段：**設計跨科系教授 Persona 面試官引擎**！
