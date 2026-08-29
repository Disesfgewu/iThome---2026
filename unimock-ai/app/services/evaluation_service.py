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
        transcript_text: str
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

        avg_dimension_score = sum(radar_scores.values()) / max(len(radar_scores), 1)
        overall_score = round(avg_dimension_score * 10, 1)

        return {
            "session_id": session_id,
            "overall_score": overall_score,
            "radar_scores": radar_scores,
            "strengths": insights["strengths"],
            "improvements": insights["improvements"],
            "scoring_evaluation_text": scoring_text,
            "overall_strategic_report": overall_text
        }

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
