from typing import Dict, Any, List, Optional
from app.services.gemma_llm import gemma_client

class AnswerOptimizerService:
    """
    Per-question Weakness Diagnosis & Exemplary Answer Optimizer Engine.
    Analyzes candidate answers for each Q/A turn, diagnoses technical gaps,
    and generates STAR-optimized high-scoring exemplar answers via Gemma-4-31B.
    """
    async def diagnose_and_optimize_turn(
        self,
        question: str,
        user_answer: str,
        target_major: str
    ) -> Dict[str, Any]:
        """
        Diagnoses a single Q&A pair and generates actionable optimization suggestions & model answer.
        """
        prompt = (
            f"【目標學系】：{target_major}\n"
            f"【考官題目】：{question}\n"
            f"【學生回答】：{user_answer}\n\n"
            "請針對以上學生回答進行深度診斷：\n"
            "1. 【扣分盲點與弱點】：指出回答中缺乏的 STAR 原則要素、專業術語不精確或邏輯不連貫之處。\n"
            "2. 【滿分優化示範回答】：根據目標學系期待，提供一份結構完整、符合 STAR 原則的高分範本回答。"
        )

        response_text = await gemma_client.invoke_with_system_prompt(
            prompt_name="overall_analysis",
            user_input=prompt,
            candidate_profile=target_major,
            target_major=target_major,
            transcript=f"[考官]: {question}\n[學生]: {user_answer}",
            aggregated_scores=""
        )

        return {
            "question": question,
            "original_answer": user_answer,
            "diagnosis_and_optimized_answer": response_text
        }

    async def batch_diagnose_transcript(
        self,
        transcript_turns: List[Dict[str, str]],
        target_major: str
    ) -> List[Dict[str, Any]]:
        """
        Batch diagnoses all turns in an interview transcript.
        """
        diagnoses = []
        for turn in transcript_turns:
            question = turn.get("question", "")
            answer = turn.get("answer", "")
            if question and answer:
                diag = await self.diagnose_and_optimize_turn(question, answer, target_major)
                diagnoses.append(diag)
        return diagnoses

answer_optimizer = AnswerOptimizerService()
