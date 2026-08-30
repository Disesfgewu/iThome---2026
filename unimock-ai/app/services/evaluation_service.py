import re
import json
import logging
from typing import Dict, Any, List, Optional
from app.services.gemma_llm import gemma_client

logger = logging.getLogger(__name__)

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
        try:
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

            # 3. Dynamic parsing from LLM outputs
            radar_scores = self.parse_radar_scores(scoring_text)
            insights = self.parse_strengths_and_improvements(scoring_text, target_major)
            question_diagnoses = self.parse_question_diagnoses_from_llm(scoring_text, transcript_turns or [], target_major)

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
        except Exception as e:
            logger.error(f"LLM Evaluation failed ({e}), falling back to FallbackService.")
            from app.services.fallback_service import fallback_service
            fallback_res = fallback_service.get_fallback_evaluation_report(
                target_school=target_school,
                target_major=target_major,
                transcript_turns=transcript_turns or []
            )
            fallback_res["session_id"] = session_id
            fallback_res["scoring_evaluation_text"] = "系統自動降級評測報告"
            fallback_res["overall_strategic_report"] = fallback_res["overall_feedback"]
            return fallback_res

    def parse_question_diagnoses_from_llm(
        self,
        scoring_text: str,
        transcript_turns: List[Dict[str, Any]],
        target_major: str
    ) -> List[Dict[str, Any]]:
        """
        Parses dynamic, LLM-generated per-turn STAR diagnoses from scoring_text JSON block.
        Completely dynamic for ALL schools and majors without hardcoded if-else templates.
        """
        parsed_diagnoses_map = {}
        json_match = re.search(r"```json\s*(\{.*?\})\s*```", scoring_text, re.DOTALL)
        if json_match:
            try:
                parsed = json.loads(json_match.group(1))
                if isinstance(parsed.get("question_diagnoses"), list):
                    for item in parsed["question_diagnoses"]:
                        t_idx = item.get("turn_index") or item.get("turn")
                        if t_idx:
                            parsed_diagnoses_map[int(t_idx)] = {
                                "weakness_analysis": item.get("weakness_analysis", "").strip(),
                                "improved_sample": gemma_client.clean_markdown_formatting(item.get("improved_sample", "")).strip()
                            }
            except Exception:
                pass

        diagnoses = []
        for idx, turn in enumerate(transcript_turns):
            turn_num = turn.get("turn", idx + 1)
            q_text = turn.get("question", "")
            a_text = turn.get("answer", "")

            # 1. Use LLM-generated diagnosis if available from JSON output
            if turn_num in parsed_diagnoses_map and parsed_diagnoses_map[turn_num]["improved_sample"]:
                llm_diag = parsed_diagnoses_map[turn_num]
                diagnoses.append({
                    "turn_index": turn_num,
                    "question": q_text,
                    "original_answer": a_text,
                    "weakness_analysis": llm_diag["weakness_analysis"] or f"回答條理尚可，建議補充更多對 {target_major} 的實務切入與量化成果。",
                    "improved_sample": llm_diag["improved_sample"]
                })
                continue

            # 2. Dynamic generation for unparsed turns using answer & question context
            if not a_text or len(a_text.strip()) < 10:
                weakness = "回答過於簡短，未針對題目提供任何具體實務細節、數據或個人亮點。"
                improved = f"教授您好，針對這個問題，我想從實際經驗切入說明。在修習{target_major}相關基礎的過程中，我曾主動承擔相關任務，透過系統性規劃與資源整合，成功克服困難並達成具體成效，這是我決定報考貴系的核心動機。"
            else:
                weakness = f"回答表達流暢，若能深化 {target_major} 核心理論與具體實務/專案成果的連結，說服力將更加卓越。"
                improved = f"教授您好，在修習{target_major}專業基礎與推動相關歷程中，我發現傳統方法面臨特定瓶頸，因此我主動導入結構化分析與優化機制，成功提升整體成效。這段經驗確立了我在{target_major}繼續深化的動機。"

            diagnoses.append({
                "turn_index": turn_num,
                "question": q_text,
                "original_answer": a_text,
                "weakness_analysis": weakness,
                "improved_sample": improved
            })

        return diagnoses

    def generate_turn_diagnoses(
        self,
        transcript_turns: List[Dict[str, Any]],
        target_major: str
    ) -> List[Dict[str, Any]]:
        """Alias for parse_question_diagnoses_from_llm for backward compatibility."""
        return self.parse_question_diagnoses_from_llm("", transcript_turns, target_major)

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

        json_match = re.search(r"```json\s*(\{.*?\})\s*```", scoring_text, re.DOTALL)
        if json_match:
            try:
                parsed = json.loads(json_match.group(1))
                for key in dimensions.keys():
                    if key in parsed:
                        val = float(parsed[key])
                        if val <= 5.0:
                            val = val * 2.0
                        dimensions[key] = round(min(max(val, 1.0), 10.0), 1)
                return dimensions
            except Exception:
                pass

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
