# 【Day 12】面試狀態機（State Machine）：四階段對話流轉機制實作

面試過程不能漫無目的發問。今天我們要為 Agent 設計一個明確的 **四階段狀態機 (State Machine)** 控制器。

---

## 1. 四階段面試對話流轉設計

```
  ┌────────────────┐
  │ 1. 自我介紹階段 │ (第一輪：破冰與申請動機)
  └───────┬────────┘
          ▼
  ┌────────────────┐
  │ 2. 備審深挖階段 │ (第二、三輪：專案與自傳疑點追問)
  └───────┬────────┘
          ▼
  ┌────────────────┐
  │ 3. 臨場情境階段 │ (第四輪：專業概念或情境反應)
  └───────┬────────┘
          ▼
  ┌────────────────┐
  │ 4. 學生反問階段 │ (第五輪：結尾與總結收尾)
  └────────────────┘
```

---

## 2. 狀態機控制器代碼草稿 (`app/services/interview_state_machine.py`)

```python
from enum import Enum
from typing import Dict, Any

class Stage(Enum):
    SELF_INTRO = 1
    RESUME_DEEP_DIVE = 2
    SITUATIONAL_QUESTION = 3
    REVERSE_QUESTION = 4
    FINISHED = 5

class InterviewStateMachine:
    def __init__(self, session_id: str):
        self.session_id = session_id
        self.current_stage = Stage.SELF_INTRO
        self.turn_count = 0

    def next_turn(self, answer: str) -> Dict[str, Any]:
        self.turn_count += 1
        
        if self.turn_count == 1:
            self.current_stage = Stage.RESUME_DEEP_DIVE
            question = "感謝你的介紹。在你的自傳中提到有參與 AI 導覽專案，請說明你主要負責的模組？"
        elif self.turn_count == 2:
            self.current_stage = Stage.RESUME_DEEP_DIVE
            question = "在這個專案中遇到了什麼挑戰？"
        elif self.turn_count == 3:
            self.current_stage = Stage.SITUATIONAL_QUESTION
            question = "如果團員進度嚴重落後，你會如何處理？"
        elif self.turn_count == 4:
            self.current_stage = Stage.REVERSE_QUESTION
            question = "最後，你有什麼問題想問我們教授嗎？"
        else:
            self.current_stage = Stage.FINISHED
            return {"next_question": None, "is_finished": True}

        return {"next_question": question, "is_finished": False, "stage": self.current_stage.name}
```

---

## 結語與明天預告

今天我們實現了面試動態狀態機控制器。

明天 **【Day 13】**，我們將注入蘇格拉底式動態追問邏輯（Dynamic Follow-up），提升 AI 面試官的質疑能力！
