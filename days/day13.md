# 【Day 13】動態追問邏輯（Dynamic Follow-up）：蘇格拉底式深入提問 Agent

當學生的回答流於表面或過於簡短時，AI 面試官不能直接跳到下一題。今天我們要設計 **蘇格拉底式動態追問邏輯 (Dynamic Follow-up)**。

---

## 1. 追問判定 Prompt 範例

```text
你是一位嚴謹的大學面試官。請評估學生剛才的回答：
【學生回答】："{candidate_answer}"

如果回答過於簡短（低於 30 字）或缺乏具體實例，請採用「蘇格拉底式追問」，針對其回答點出疑問並要其補充：
- 為什麼（Why）做這個選擇？
- 具體（How）是如何實作的？
- 獲得了什麼（What）量化結果？
```

---

## 2. 追問邏輯與程式碼實現 (`app/services/followup_agent.py`)

```python
from app.services.gemma_client import ResilientGemmaClient

class FollowupAgent:
    def __init__(self):
        self.client = ResilientGemmaClient()

    def evaluate_and_generate_followup(self, question: str, answer: str) -> str:
        if len(answer.strip()) < 20:
            return f"你的回答似乎有點簡略。能請你針對剛才提到的『{answer[:10]}...』進一步說明具體過程嗎？"
        
        # 呼叫 Gemma 生成高質量二階追問
        return f"聽起來很有收穫！那麼在這個過程中，如果重新做一次，你會做什麼調整？"
```

---

## 結語與明天預告

今天我們增強了 AI 面試官的脈絡追問與邏輯辨析能力。

明天 **【Day 14】**，我們將整合 LangChain Conversation Memory，維護對話歷史與 Token 滑動視窗！
