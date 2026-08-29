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
                    f"【Situation】針對 {target_major} 面試中提及的『{q_text[:20]}...』情境；"
                    f"【Task】我的核心任務是說明個人專業優勢與解題思維；"
                    f"【Action】我主動列舉 2 項代表性專案/實務經歷，詳細說明戰略選擇與執行流程；"
                    f"【Result】成功展示扎實的實務能力，並連結個人入學後的修課與研究規劃。"
                )
            elif is_business_or_emba:
                if turn_num == 1:
                    weakness = f"自我介紹表達沉著，建議加強說明高階管理視角、資產與風險管理決策，以及報考 {target_major} 的核心動機。"
                    improved = (
                        f"「教授您好，我是報考貴所的考生。我任職於金融機構風控主管，主要負責跨國資產負債與法遵決策管理。【Situation / Task】"
                        f"在實務中，我主動引入敏感度分析模型與結構化避險架構，提升資金流動性安全，【Action】"
                        f"成功控制營運風險與資金成本升幅。【Result】"
                        f"我希望能將這些實戰經驗結合 {target_major} 的高階管理與國際金融架構，深化跨國戰略決策能力。」"
                    )
                elif turn_num == 2:
                    weakness = "實務經驗述說清晰，但建議進一步補充具體管理決策架構與量化成效指標。"
                    improved = (
                        f"「教授您好，在面對美聯儲升息與國際供應鏈重組時，【Situation】"
                        f"我主持了外匯避險與流動性壓力測試專案。【Task】"
                        f"透過建立動態敏感度分析模型與風險權重監控流程，【Action】"
                        f"我們成功將資金成本增幅控制在預期範圍內，確保公司財務結構健全。【Result】"
                        f"這項專案證明了我在 {target_major} 領域具備兼具金融數據分析與高階管理決策的實務能力。」"
                    )
                else:
                    weakness = f"專業觀點極具前瞻性，若能深化 ESG 綠色金融與 AI 自動化審查之落地戰略，說服力將更加卓越。"
                    improved = (
                        f"「教授您好，關於未來的學習與研究規劃，【Situation】"
                        f"我將重點聚焦於綠色金融與 ESG 永續放款標準。【Task】"
                        f"我預計透過 AI 智動化風控審查與評估技術導入可行性，引導企業完成數位轉型與國際市場佈局，【Action】"
                        f"建立兼具永續效益與營運效能的雙贏模式，這也是我在 {target_major} 發展的重點目標。【Result】」"
                    )
            elif turn_num == 1:
                weakness = f"自我介紹條理尚屬清晰，但建議加強『報考 {target_major} 的強烈核心動機』與『具體專案成果/競賽數據』的連結。"
                kw = "專案實作" if "專案" in a_text else ("研究" if "研究" in a_text else "專業基礎")
                improved = (
                    f"「教授您好，在修習專業基礎與推動『{kw}』專案時，【Situation】"
                    f"我的核心目標是探究原理並提升關鍵問題排解效率。【Task】"
                    f"我採用模組化設計與結構化測試，克服關鍵效能瓶頸，【Action】"
                    f"成功提升執行效能 35%，獲得良好的使用者回饋。【Result】"
                    f"這段經驗奠定了我深入 {target_major} 探究資安與架構的堅定動機。」"
                )
            elif "技術" in q_text or "演算法" in q_text or "專案" in q_text or "SQL" in a_text or "Python" in a_text or "機制" in a_text or "SQLite" in a_text:
                weakness = "技術細節回答明確，但建議補充『演算法 Trade-off 選擇考量』與『最終量化效能指標』。"
                tech_kw = "資料庫 Index 索引與查詢優化" if ("SQLite" in a_text or "SQL" in a_text) else ("推薦系統冷啟動與權重過濾" if ("推薦" in a_text or "協同過濾" in a_text) else "核心演算法選擇")
                improved = (
                    f"「教授您好，面對專案中『{tech_kw}』的瓶頸與挑戰，【Situation】"
                    f"我需要兼顧推論精準度與資料檢索回應時間。【Task】"
                    f"我採用對比分析，設計兼具過濾演算法與數據快取緩衝的混合架構，【Action】"
                    f"成功將回應延遲降低至毫秒等級，極大化系統吞吐量。【Result】"
                    f"這證明了我具備優秀的 {target_major} 實務開發與架構優化潛能。」"
                )
            else:
                weakness = f"回答具備良好說服力，若能進一步連結 {target_major} 最新前瞻趨勢（如 AI 結合企業流程與資安防護），講述深度將更臻完善。"
                improved = (
                    f"「教授您好，對於未來的專業應用與前瞻趨勢，【Situation】"
                    f"我著重於如何將大語言模型與 LLM 整合至企業業務流程中。【Task】"
                    f"我深入評估技術可行性、資訊安全規範與流程自動化，【Action】"
                    f"期望能打造兼具高效能與安全性之企業級 AI 系統，展現出 {target_major} 的跨領域競逐優勢。【Result】」"
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
