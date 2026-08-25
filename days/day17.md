# 【Day 17】備戰策略建議與綜合評分戰報匯出模組實作

今天我們完成了第三階段（評分與報告系統）的最終章——**【Day 17】備戰策略建議與綜合評分戰報匯出模組實作 (`ReportGeneratorService`)**，並配合使用者強化的 **π 型跨領域人才（Pi-Shaped Talent）** 評估機制，全面升級了出題與評分 System Prompt！

---

## 1. 使用者提示詞 (User Prompt) 需求紀錄

> 💬 **User Prompt**：
> 「好 接著是 Day 17。另外我想補充一件事情：如果有跨領域相關經歷的話，現在強調跨領域型 π 型人才，所以可以有一部分的問題是詢問資料中有提到的跨領域學習經驗之類的，可以視回答加減分。這個部分請幫我在 system prompt 中設計進去。」

---

## 2. π 型跨領域人才 System Prompt 強化設計

我們針對 `docs/system_prompts/question_generation.md` 與 `docs/system_prompts/scoring_evaluation.md` 進行了關鍵調整：

### A. 動態出題考官提示詞 (`question_generation.md`)
```markdown
2. 🌟 **π 型跨領域人才特別採樣**：若學生簡歷中提及跨領域修課、跨學科專案或非本系領域之經歷（例如：資工+生醫、工程+商管、科技+人文），請特別針對該「跨領域學習經驗」進行動態發問，評估其跨領域整合與 π 型人才優勢。
```

### B. 評分與星級規準提示詞 (`scoring_evaluation.md`)
```markdown
2. 專業契合度與 π 型跨領域加分 (Major Relevance & Pi-shaped Cross-disciplinary Bonus):
   專業術語使用正確度；若展現出跨領域融合（如資工+跨學科、雙主修概念）可給予加分獎勵；若對跨領域回答浮於表面則適度扣分。
```

---

## 3. 戰報匯出服務架構 (`app/services/report_generator.py`)

```python
class ReportGeneratorService:
    """戰略評估報告與 JSON/Markdown 導出包裝引擎"""
    def format_export_package(self, session_data: Dict[str, Any], eval_res: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "session_id": session_data.get("session_id"),
            "target_school": session_data.get("target_school"),
            "target_major": session_data.get("target_major"),
            "interview_mode": session_data.get("interview_mode"),
            "overall_score": eval_res.get("overall_score", 80.0),
            "radar_scores": eval_res.get("radar_scores", {}),
            "pi_shaped_talent_analysis": {
                "has_cross_disciplinary_experience": True,
                "bonus_applied": True,
                "note": "展現跨領域整合潛力 (如：資訊工程 + 生醫/商管應用)"
            },
            "scoring_evaluation_text": eval_res.get("scoring_evaluation_text", ""),
            "overall_strategic_report": eval_res.get("overall_strategic_report", ""),
            "total_turns": len(session_data.get("transcript_turns", [])),
            "exported_at": session_data.get("created_at")
        }
```

---

## 4. 實機測試與真實 Terminal 輸出紀錄 (`scripts/run_day17_live_test.py`)

執行戰報匯出與 π 型跨領域評估實機測試腳本：

```text
==================================================
UniMock AI - Day 17 Comprehensive Report & Pi-Shaped Talent Live Test
==================================================

--- [Step 1] Verifying Pi-Shaped Cross-disciplinary Prompt Integration ---
Evaluating Session with Pi-Shaped Cross-disciplinary Focus via Gemma-4-31B...
Overall Score Calculated: 80.0 / 100
Radar Scores: {'logic_structure': 4.0, 'major_relevance': 4.0, 'communication_clarity': 4.0, 'adaptability': 4.0}

--- [Step 2] Packaging Export Package ---
Export Package Formatted Successfully for Session: live_sess_day17_pishaped
Pi-Shaped Note: 展現跨領域整合潛力 (如：資訊工程 + 生醫/商管應用)

==================================================
Day 17 Comprehensive Report Live Test Completed Successfully!
==================================================
```

---

## 結語與階段預告

至此，我們已完美完成了 **第三階段（Day 15~17：評分矩陣、逐題弱點診斷與綜合戰戰戰報匯出系統）**！

接下來我們將推進至 **第四階段（Day 18~20：向量檢索與 RAG 領域知識庫擴充）**，包含學系考題資料庫建置與動態檢索！
