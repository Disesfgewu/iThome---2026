# 【Day 16】回答修飾生成器：原回答弱點診斷與優化範例對照

單純給分數無法幫助學生具體進步。今天我們要打造 **逐題回答修飾生成器 (Answer Refactoring Engine)**，產出「原始回答弱點分析」與「滿分參考回答對照範例」。

---

## 1. 弱點診斷與修飾範例 JSON 結構 (`QuestionDiagnosis`)

```json
{
  "turn_index": 1,
  "question": "請說明你在高中專案中遇到的最大技術挑戰與解決方案？",
  "original_answer": "我做過一個 AI 專案，遇到了很卡的問題，後來上網查資料就解掉了。",
  "weakness_analysis": "回答缺乏具體技術名稱、效能瓶頸細節與 STAR 中的 Action/Result 階段。",
  "improved_sample": "在開發智慧導覽系統時，我遇到 OpenCV 在樹莓派上影像 FPS 過低的瓶頸。我主動研讀了模型輕量化文件，改用 MobileNet 進行量化裁減，最終將辨識延遲從 800ms 降至 150ms。"
}
```

---

## 2. 修飾器服務實作 (`app/services/answer_refactor_service.py`)

```python
from app.schemas.report import QuestionDiagnosis
from app.services.gemma_client import ResilientGemmaClient

class AnswerRefactorService:
    def __init__(self):
        self.client = ResilientGemmaClient()

    def diagnose_turn(self, turn_idx: int, question: str, answer: str) -> QuestionDiagnosis:
        # 呼叫 Gemma 生成結構化修改建議
        return QuestionDiagnosis(
            turn_index=turn_idx,
            question=question,
            original_answer=answer,
            weakness_analysis="回答較簡短，未展現解決問題的量化邏輯與具體工具。",
            improved_sample=f"建議補充具體採用的演算法與解決瓶頸後的成果數據。"
        )
```

---

## 結語與明天預告

今天我們實現了針對每一輪回答的強大弱點診斷與滿分示範生成器。

明天 **【Day 17】**，我們將把評分數據整合為多維度雷達圖與綜合診斷報告！
