# 【Day 13】面試流程與對話品質持續優化：蘇格拉底式動態追問機制實作

在 Day 12 建立了四階段狀態機後，今天我們針對 AI 面試官的**對話品質與追問動態性 (Dialogue Quality & Socratic Follow-up)** 進行深度優化，解決學生回答過於簡短、含糊或缺乏 STAR 原則細節時的面試品質問題。

---

## 1. 使用者提示詞 (User Prompt) 與優化需求

> 💬 **User Prompt**：
> 「接下來是 Day 13 持續優化這個面試流程跟設計。如果回答過於簡短（低於 30 字）或缺乏具體實例，請採用『蘇格拉底式追問』，針對其回答點出疑問並要其補充：
> - 為什麼 (Why) 做這個選擇？
> - 具體 (How) 是如何實作的？
> - 獲得了什麼 (What) 量化結果？」

---

## 2. 蘇格拉底式追問機制架構 (Socratic Probe Architecture)

```mermaid
graph TD
    A["學生提交回答 (/api/interview/answer)"] --> B["FollowupAgent 回答品質評估"]
    B -->|長度 < 30 字 OR STAR 分數 <= 1| C["觸發蘇格拉底式追問指引 (Why / How / What)"]
    B -->|回答結構完整 (STAR 得分 3 分)| D["推進下一階段常態發問"]
    C --> E["注入 Socratic Prompt 指引至 Gemma-4-31B"]
    D --> E
    E --> F["生成具體引導與循循善誘追問問題"]
```

---

## 3. 核心機制實作程式碼片段 (`app/services/followup_agent.py`)

```python
class FollowupAgent:
    """評估學生回答品質，動態生成蘇格拉底式追問 Prompt 指引"""
    def evaluate_answer_quality(self, answer: str) -> Dict[str, Any]:
        clean_text = answer.strip()
        length = len(clean_text)
        is_too_brief = length < 30

        has_action = any(kw in clean_text for kw in ["使用", "採用", "實作", "開發", "優化", "設計", "解決"])
        has_result = any(kw in clean_text for kw in ["成果", "提升", "縮短", "降低", "獎項", "效率"])

        star_score = (1 if length >= 30 else 0) + (1 if has_action else 0) + (1 if has_result else 0)
        requires_socratic_probe = is_too_brief or star_score <= 1

        return {"length": length, "is_too_brief": is_too_brief, "star_score": star_score, "requires_socratic_probe": requires_socratic_probe}

    def build_socratic_prompt(self, question: str, answer: str, quality_eval: Dict[str, Any]) -> str:
        if quality_eval["is_too_brief"]:
            return (
                "【考官觀察】：學生的回答過於簡短，缺乏具體技術細節。\n"
                "【蘇格拉底追問指引】：請點出問題並引導追問：1. 為什麼 (Why) 做此選擇？ 2. 具體 (How) 如何克服困難？"
            )
        elif quality_eval["star_score"] <= 1:
            return "【考官觀察】：回答缺乏具體行動 (Action) 或成果 (Result)。請追問其演算法權衡 (Trade-off) 與實質成果 (What)。"
        return "【考官觀察】：回答結構完整，請深化技術點並順暢推動面試。"
```

### 整合至 FastAPI 控制器 (`app/routers/interview.py`)

```python
@router.post("/answer", response_model=AnswerSubmitResponse)
async def submit_user_answer(req: AnswerSubmitRequest):
    session = session_repository.get_session(req.session_id)
    session_repository.add_answer_turn(req.session_id, req.user_answer)

    # 1. 執行 FollowupAgent 品質評估與蘇格拉底指引生成
    quality_eval = followup_agent.evaluate_answer_quality(req.user_answer)
    socratic_instruction = followup_agent.build_socratic_prompt(session["transcript_turns"][-1]["question"], req.user_answer, quality_eval)

    # 2. 結合狀態機指引與蘇格拉底指引
    turn_count = len(session["transcript_turns"]) + 1
    next_stage, is_finished = interview_state_machine.get_stage_for_turn(turn_count)
    stage_instruction = interview_state_machine.get_stage_instruction(next_stage)

    user_prompt_with_instructions = f"{stage_instruction}\n{socratic_instruction}\n【學生最新回答】：{req.user_answer}"

    next_question = await gemma_client.invoke_with_system_prompt("response_generation", user_input=user_prompt_with_instructions, target_major=session["target_major"], candidate_profile=session["candidate_profile"].to_structured_text(), transcript=token_context_guard.truncate_transcript(session["transcript_text"]))
    session_repository.add_question_turn(req.session_id, next_question)

    return AnswerSubmitResponse(session_id=req.session_id, user_answer=req.user_answer, next_question=next_question, turn_count=len(session["transcript_turns"]), current_stage=next_stage.value, is_finished=is_finished)
```

---

## 4. 實機測試與真實 Terminal 輸出紀錄 (`scripts/run_day13_live_test.py`)

執行對話品質優化測試腳本，模擬學生僅回答 4 個字（`"就寫程式。"`）時觸發蘇格拉底式動態追問：

```text
==================================================
UniMock AI - Day 13 Socratic Followup Optimization Live Test
==================================================

--- [Step 1] Verifying FollowupAgent Quality Evaluation ---
Brief Answer Evaluation: Length=7 | Too Brief=True | Socratic Probe Needed=True
Complete Answer Evaluation: Length=56 | STAR Score=3 | Socratic Probe Needed=False

--- [Step 2] Live FastAPI Socratic Followup Triggering ---
Session Created: sess_5b21d3d207 | First Question Generated.

Socratic Follow-up Question Generated:
[考官]：（微微調整眼鏡，表情溫和但眼神銳利，身體稍微前傾，以鼓勵且耐心的語氣說道：）

「嗯，我知道在專案執行過程中，寫程式確實是核心的工作。不過，對於我們教授來說，比起『做了什麼』，我們更感興趣的是你在寫程式過程中的『思考邏輯』與『解決問題的能力』。」

「所以，我想請你試著把這個過程具體化。比如，在這次的專案中，你選擇使用哪一種程式語言或框架？為什麼選擇它而不是其他的工具？另外，在寫程式的過程中，一定會遇到讓你卡住的 Bug 或是邏輯上很困難的地方，能不能分享一個具體的技術困難，以及你當時是如何一步步分析並克服它的？請試著詳細描述給我聽。」

==================================================
Day 13 Socratic Followup Live Test Completed Successfully!
==================================================
```

---

## 結語與明天預告

今天我們完成了 **面試流程與對話品質持續優化 (`FollowupAgent`)**，透過自動化的回答長度與 STAR 原則檢驗，成功讓 AI 面試官在遇到學生過度簡短或模糊的回答時，能自動觸發具備教育引導性的「蘇格拉底式追問」！

明天 **【Day 14】**，我們將正式進入 **前後端 SSE 串流連通與前端對話 UI 的整合測試 (Server-Sent Events & Frontend UI Streaming)**！
