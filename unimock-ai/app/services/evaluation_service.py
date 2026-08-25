import re
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

        # 3. Extract radar chart scores
        radar_scores = self.parse_radar_scores(scoring_text)
        overall_score = round(sum(radar_scores.values()) / len(radar_scores) * 20, 1)

        return {
            "session_id": session_id,
            "overall_score": overall_score,
            "radar_scores": radar_scores,
            "scoring_evaluation_text": scoring_text,
            "overall_strategic_report": overall_text
        }

    def parse_radar_scores(self, scoring_text: str) -> Dict[str, float]:
        """
        Extracts 1~5 star numerical ratings for the 4 dimensions from Gemma 4 output,
        defaulting to 4.0 if unstructured.
        """
        dimensions = {
            "logic_structure": 4.0,
            "major_relevance": 4.0,
            "communication_clarity": 4.0,
            "adaptability": 4.0
        }
        
        # Regex search for star counts or ratings
        logic_match = re.search(r"邏輯[^\n]*?([1-5])\s*?[星★分]", scoring_text)
        if logic_match:
            dimensions["logic_structure"] = float(logic_match.group(1))

        relevance_match = re.search(r"專業[^\n]*?([1-5])\s*?[星★分]", scoring_text)
        if relevance_match:
            dimensions["major_relevance"] = float(relevance_match.group(1))

        clarity_match = re.search(r"表達[^\n]*?([1-5])\s*?[星★分]", scoring_text)
        if clarity_match:
            dimensions["communication_clarity"] = float(clarity_match.group(1))

        adaptability_match = re.search(r"應變[^\n]*?([1-5])\s*?[星★分]", scoring_text)
        if adaptability_match:
            dimensions["adaptability"] = float(adaptability_match.group(1))

        return dimensions

evaluation_service = EvaluationService()
