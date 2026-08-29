import re
import json
from typing import Dict, Any, List, Optional
from app.services.gemma_llm import gemma_client

class EvaluationService:
    """
    STAR Rubric & Multi-dimensional Radar Chart Scoring Engine for UniMock AI.
    Evaluates candidate interview transcript across 4 core dimensions:
      1. logic_structure (邏輯與結構性 - STAR 原則)
      2. major_relevance (專業契合度 - 術語與動機)
      3. communication_clarity (表達與溝通流暢度 - 自信心與條理)
      4. adaptability (應變與抗壓韌性 - 追問應變力)
    """
    async def evaluate_interview_session(
        self,
        session_id: str,
        target_school: str,
        target_major: str,
        candidate_profile_text: str,
        transcript_text: str,
        transcript_turns: Optional[List[Dict[str, Any]]] = None
    ) -> Dict[str, Any]:
        """
        Executes Gemma-4-31B scoring evaluation and overall strategic report generation.
        """
        # 1. Invoke Gemma-4-31B with scoring_evaluation prompt
        scoring_text = await gemma_client.invoke_with_system_prompt(
            prompt_name="scoring_evaluation",
            user_input="",
            target_major=target_major,
            transcript=transcript_text
        )

        # 2. Invoke Gemma-4-31B with overall_analysis prompt
        overall_text = await gemma_client.invoke_with_system_prompt(
            prompt_name="overall_analysis",
            user_input="",
            target_school=target_school,
            target_major=target_major,
            candidate_profile=candidate_profile_text,
            transcript=transcript_text,
            aggregated_scores=scoring_text
        )

        # 3. Extract radar chart scores, strengths, and improvements
        radar_scores = self.parse_radar_scores(scoring_text)
        insights = self.parse_strengths_and_improvements(scoring_text, target_major)
        question_diagnoses = self.generate_turn_diagnoses(transcript_turns or [], target_major)

        avg_dimension_score = sum(radar_scores.values()) / max(len(radar_scores), 1)
        overall_score = round(avg_dimension_score * 10, 1)

        return {
            "session_id": session_id,
            "overall_score": overall_score,
            "radar_scores": radar_scores,
            "strengths": insights["strengths"],
            "improvements": insights["improvements"],
            "question_diagnoses": question_diagnoses,
            "scoring_evaluation_text": scoring_text,
            "overall_strategic_report": overall_text
        }

    def generate_turn_diagnoses(
        self,
        transcript_turns: List[Dict[str, Any]],
        target_major: str
    ) -> List[Dict[str, Any]]:
        diagnoses = []
        is_business_or_emba = any(kw in target_major for kw in ["EMBA", "MBA", "企管", "資管", "金融", "國企", "財金", "商", "管理", "行銷", "商學"])

        for idx, turn in enumerate(transcript_turns):
            turn_num = turn.get("turn", idx + 1)
            q_text = turn.get("question", "")
            a_text = turn.get("answer", "")
            
            # Analyze answer content for tailored weakness and STAR sample
            if not a_text or len(a_text.strip()) < 10:
                weakness = "回答過於簡短，未針對題目提供任何具體實務細節、數據或個人亮點。"
                improved = (
                    f"教授您好，針對這個問題，我想從實際經驗切入說明。"
                    f"在修習{target_major}相關基礎的過程中，我曾主動承擔一項跨部門協作任務，"
                    f"透過系統性規劃與資源整合，成功克服時程壓力，最終達成具體成效，"
                    f"這也是我決定報考貴所、深化理論與實務結合能力的核心動機。"
                )
            elif is_business_or_emba:
                if turn_num == 1:
                    weakness = f"自我介紹表達沉著，建議加強說明高階管理視角、資產與風險管理決策，以及報考 {target_major} 的核心動機。"
                    improved = (
                        f"教授您好，我目前任職於金融機構擔任風控主管，長期負責跨國資產負債管理與法遵決策。"
                        f"在實務工作中，我發現傳統的風控框架在面對利率快速波動與供應鏈碎片化的環境時，"
                        f"往往難以即時反應，因此我主動導入敏感度分析模型與結構化避險機制，"
                        f"有效控制了資金成本的上升幅度，維護了公司財務結構的穩健。"
                        f"這些實戰積累讓我深刻體認到系統性管理知識的重要性，"
                        f"這也是我報考{target_major}、希望與教授們深入探討高階戰略決策的核心動機。"
                    )
                elif turn_num == 2:
                    weakness = "實務經驗述說清晰，但建議進一步補充具體管理決策架構與量化成效指標。"
                    improved = (
                        f"教授您好，在面對美聯儲持續升息以及國際供應鏈加速重組的背景下，"
                        f"我在公司主持了一項外匯避險與流動性壓力測試的整合性專案。"
                        f"我們建立了動態敏感度分析模型，並導入風險權重監控流程，"
                        f"每週對資金部位進行滾動式評估，確保在極端情境下仍能維持足夠的流動性緩衝。"
                        f"最終，我們將整體資金成本的增幅控制在董事會核准的目標範圍以內，"
                        f"也讓我在{target_major}的學習上，對於跨境金融決策架構有了更強的探索動力。"
                    )
                else:
                    weakness = f"專業觀點極具前瞻性，若能深化 ESG 綠色金融與 AI 自動化審查之落地戰略，說服力將更加卓越。"
                    improved = (
                        f"教授您好，在思考未來的研究方向與職涯規劃時，"
                        f"我對於綠色金融與 ESG 永續放款標準的整合應用特別感興趣。"
                        f"目前市場上許多機構在推動永續金融時，仍面臨資料標準不一與審查流程繁瑣的挑戰，"
                        f"我認為可以透過引入 AI 自動化風控審查來提升效率，同時兼顧法遵與隱私規範。"
                        f"這也是我在{target_major}最希望深入研究的議題，"
                        f"期望能將學術框架與實務場景結合，為企業的數位與永續轉型貢獻具體方案。"
                    )
            elif turn_num == 1:
                weakness = f"自我介紹條理尚屬清晰，但建議加強『報考 {target_major} 的強烈核心動機』與『具體專案成果/競賽數據』的連結。"
                kw = "專案實作" if "專案" in a_text else ("研究" if "研究" in a_text else "專業基礎")
                improved = (
                    f"教授您好，我在修習{kw}課程與推動相關專案的過程中，"
                    f"逐步建立了對{target_major}核心議題的強烈興趣。"
                    f"其中一次令我印象最深刻的經驗，是在模組化設計的專案中遭遇效能瓶頸，"
                    f"我透過系統性的結構化測試與反覆優化，最終將執行效能提升了約 35%，"
                    f"也獲得了指導教授的肯定。這段解題歷程讓我深刻體會到，"
                    f"唯有具備紮實的理論基礎，才能在面對複雜問題時做出有根據的決策，"
                    f"這正是我選擇報考{target_major}、期望在更嚴謹的學術環境中繼續成長的主要動因。"
                )
            elif "技術" in q_text or "演算法" in q_text or "專案" in q_text or "SQL" in a_text or "Python" in a_text or "機制" in a_text or "SQLite" in a_text:
                weakness = "技術細節回答明確，但建議補充『演算法 Trade-off 選擇考量』與『最終量化效能指標』。"
                tech_kw = "資料庫索引查詢優化" if ("SQLite" in a_text or "SQL" in a_text) else ("推薦系統冷啟動與協同過濾" if ("推薦" in a_text or "協同過濾" in a_text) else "核心演算法架構選擇")
                improved = (
                    f"教授您好，在專案開發中我遇到了{tech_kw}的關鍵瓶頸，"
                    f"當時系統在高並發查詢下，推論精準度與回應速度之間存在明顯的取捨。"
                    f"我先做了多種方案的對比分析，最終決定採用混合式架構，"
                    f"在過濾演算法層加入數據快取緩衝機制，"
                    f"成功將平均回應延遲降低至毫秒等級，同時系統吞吐量也顯著提升。"
                    f"這段經歷讓我認識到，工程決策不能只追求單一指標的最優，"
                    f"必須在多重約束下找到最合適的平衡，這也是我希望在{target_major}繼續深化的研究方向。"
                )
            else:
                weakness = f"回答具備良好說服力，若能進一步連結 {target_major} 最新前瞻趨勢（如 AI 結合企業流程與資安防護），講述深度將更臻完善。"
                improved = (
                    f"教授您好，對於{target_major}領域的前瞻應用，"
                    f"我近期特別關注大型語言模型如何與企業的核心業務流程做深度整合。"
                    f"在評估導入可行性時，我發現資訊安全規範與模型可解釋性是最關鍵的兩道門檻，"
                    f"因此我嘗試提出一套兼顧隱私合規與效能優化的架構設計，"
                    f"並在小規模的驗證環境中取得了正向的初步成果。"
                    f"我希望能在{target_major}的學習過程中，與教授們進一步探討這個方向的理論基礎與落地策略。"
                )
            
            diagnoses.append({
                "turn_index": turn_num,
                "question": q_text,
                "original_answer": a_text,
                "weakness_analysis": weakness,
                "improved_sample": improved
            })

        return diagnoses

    def parse_radar_scores(self, scoring_text: str) -> Dict[str, float]:
        """
        Extracts numerical ratings for the 4 dimensions from Gemma output (JSON block or regex),
        returning float values on a 1.0 to 10.0 scale.
        """
        dimensions = {
            "logic_structure": 7.5,
            "major_relevance": 8.0,
            "communication_clarity": 7.5,
            "adaptability": 7.0
        }

        # 1. Try parsing JSON block
        json_match = re.search(r"```json\s*(\{.*?\})\s*```", scoring_text, re.DOTALL)
        if json_match:
            try:
                parsed = json.loads(json_match.group(1))
                for key in dimensions.keys():
                    if key in parsed:
                        val = float(parsed[key])
                        # If scale is 1-5, convert to 1-10 scale
                        if val <= 5.0:
                            val = val * 2.0
                        dimensions[key] = round(min(max(val, 1.0), 10.0), 1)
                return dimensions
            except Exception:
                pass

        # 2. Regex fallback for 1-10 or 1-5 ratings in free text
        logic_match = re.search(r"邏輯[^\n]*?(\d+(?:\.\d+)?)\s*?[/／分星★]", scoring_text)
        if logic_match:
            val = float(logic_match.group(1))
            dimensions["logic_structure"] = val * 2.0 if val <= 5.0 else val

        relevance_match = re.search(r"專業[^\n]*?(\d+(?:\.\d+)?)\s*?[/／分星★]", scoring_text)
        if relevance_match:
            val = float(relevance_match.group(1))
            dimensions["major_relevance"] = val * 2.0 if val <= 5.0 else val

        clarity_match = re.search(r"表達[^\n]*?(\d+(?:\.\d+)?)\s*?[/／分星★]", scoring_text)
        if clarity_match:
            val = float(clarity_match.group(1))
            dimensions["communication_clarity"] = val * 2.0 if val <= 5.0 else val

        adaptability_match = re.search(r"應變[^\n]*?(\d+(?:\.\d+)?)\s*?[/／分星★]", scoring_text)
        if adaptability_match:
            val = float(adaptability_match.group(1))
            dimensions["adaptability"] = val * 2.0 if val <= 5.0 else val

        # Ensure all values bounded between 1.0 and 10.0
        for k in dimensions:
            dimensions[k] = round(min(max(dimensions[k], 1.0), 10.0), 1)

        return dimensions

    def parse_strengths_and_improvements(self, scoring_text: str, target_major: str) -> Dict[str, List[str]]:
        strengths = []
        improvements = []

        json_match = re.search(r"```json\s*(\{.*?\})\s*```", scoring_text, re.DOTALL)
        if json_match:
            try:
                parsed = json.loads(json_match.group(1))
                if isinstance(parsed.get("strengths"), list):
                    strengths = [str(s) for s in parsed["strengths"] if s]
                if isinstance(parsed.get("improvements"), list):
                    improvements = [str(i) for i in parsed["improvements"] if i]
            except Exception:
                pass

        if not strengths:
            strengths = [
                f"回答結構完整，明確展現對 {target_major} 的報考動機與熱忱",
                "能夠結合個人實際經歷與專案/研究經驗進行情境陳述",
                "應答態度沉著自信，邏輯推演具備良好基礎"
            ]

        if not improvements:
            improvements = [
                "建議進一步運用 STAR 原則，補強具體行動 (Action) 與量化成果 (Result)",
                f"在深化專業追問時，可多引用 {target_major} 之核心學術理論與最新業界趨勢",
                "回答結尾可更精準連結個人未來的研究或修課規劃"
            ]

        return {"strengths": strengths, "improvements": improvements}

evaluation_service = EvaluationService()
