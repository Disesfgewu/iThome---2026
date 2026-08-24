# 【Day 15】面試評測大腦（Rubric Evaluator）：STAR 原則與評分維度設計

當多輪模擬面試結束後，系統必須產出具備權威性與教育指引價值的評測報告。今天我們要設計基於 **STAR 原則 (Situation, Task, Action, Result)** 的 Rubric 評分大腦。

---

## 1. 四大評分維度 (Rubrics)

1. **STAR 邏輯條理性 (1-10)：** 回答是否具備情境背景、任務目標、行動步驟與量化結果？
2. **科系專業契合度 (1-10)：** 表達的知識與專案經歷是否符合作為該學系學生的期待？
3. **表達清晰度 (1-10)：** 口條是否順暢、是否冗長贅字過多？
4. **臨場應變力 (1-10)：** 面對質疑或情境追問時是否能條理分明地說明？

---

## 2. Pydantic Output Parser 評分實作 (`app/services/evaluator.py`)

```python
from langchain_core.output_parsers import PydanticOutputParser
from app.schemas.report import EvaluationReport, RubricScore

class RubricEvaluator:
    def __init__(self):
        self.parser = PydanticOutputParser(pydantic_object=EvaluationReport)

    def generate_eval_prompt(self, transcript: str) -> str:
        return f"""你是一位專業的大學入學面試評審。請針對以下完整面試逐字稿進行多維度評分：
{transcript}

請遵循以下 JSON Schema 輸出格式：
{self.parser.get_format_instructions()}
"""
```

---

## 結語與明天預告

今天我們設計了基於 STAR 原則的四維度評分規準。

明天 **【Day 16】**，我們將實作「逐題弱點診斷與優化回答生成器」！
