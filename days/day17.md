# 【Day 17】雷達圖數據與綜合診斷書生成引擎

今天我們要將前面的評分數據、逐題診斷與強弱點分析，組裝成前端圖表庫（如 Chart.js / ECharts）可直接繪製多維度雷達圖的 **綜合診斷報告 (EvaluationReport)**。

---

## 1. 診斷報告 Schema 與數據格式

```python
from app.schemas.report import EvaluationReport, RubricScore, QuestionDiagnosis

def build_sample_report() -> EvaluationReport:
    return EvaluationReport(
        scores=RubricScore(
            logic_structure=8,
            major_relevance=9,
            communication_clarity=8,
            adaptability=7
        ),
        overall_feedback="整體表現亮眼，動機明確且對目標科系熱情十足。建議在臨場追問時保持鎮定並正面回應技術細節。",
        strengths=[
            "對專案技術動機強烈，自主學習能力突出",
            "對目標申請學系的未來發展規劃清晰"
        ],
        improvements=[
            "遇到效能瓶頸質疑時稍顯緊張",
            "回答中可增加更多數據績效（如 % 數提升）"
        ],
        question_diagnoses=[]
    )
```

---

## 2. 雷達圖視覺化 JSON 轉換服務 (`app/services/report_generator.py`)

```python
class ReportGeneratorService:
    def format_for_radar_chart(self, report: EvaluationReport) -> dict:
        return {
          "labels": ["邏輯條理性", "專業契合度", "表達清晰度", "臨場應變力"],
          "datasets": [{
            "label": "模擬面試成績",
            "data": [
              report.scores.logic_structure,
              report.scores.major_relevance,
              report.scores.communication_clarity,
              report.scores.adaptability
            ]
          }]
        }
```

---

## 結語與明天預告

今天我們打通了綜合診斷報告生成與前端雷達圖數據格式轉換。

明天 **【Day 18】**，我們將打造安全防護網，實作 Prompt Injection 防禦與個資過濾中介軟體！
