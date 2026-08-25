import asyncio
from typing import List, Dict, Any, Optional, Union

from app.models.candidate_model import CandidateProfile
from app.services.embedding_service import embedding_service
from app.repositories.question_repository import question_repository
from app.services.gemma_llm import gemma_client

class RAGRetrieverService:
    """
    RAG (Retrieval-Augmented Generation) Service for UniMock AI.
    
    1. Comprehensive Resume Profile Vectorization: Embeds Candidate Profile 
       (Autobiography, Experiences, Grades, Coursework, Leadership, Projects, Research, Skills)
       via Gemini Embedding 2 (3072 dims).
    2. RAG Hybrid Similarity Search: Queries pre-embedded DB vectors with candidate vector + department filtering.
    3. RAG Seed Formatting: Formats top-K questions, STAR reference answers, and rubrics for LLM injection.
    4. End-to-End LLM Question Generation: Integrates strictly with GemmaLLMClient (gemma-4-31b-it).
    """
    def __init__(self):
        self.embedding = embedding_service
        self.repository = question_repository

    async def retrieve_sample_questions_for_candidate(
        self,
        candidate_profile: Union[str, CandidateProfile],
        target_major: Optional[str] = None,
        target_school: Optional[str] = None,
        top_k: int = 3
    ) -> List[Dict[str, Any]]:
        """
        Asynchronously vectorizes full Candidate Profile and retrieves Top-K similar sample questions from DB.
        """
        if isinstance(candidate_profile, CandidateProfile):
            profile_text = candidate_profile.to_structured_text()
            major = target_major or candidate_profile.target_major
        else:
            profile_text = str(candidate_profile)
            major = target_major

        query_text = f"目標學系: {major or ''}。\n【全方位履歷歷程】\n{profile_text}"
        
        # 1. 計算全方位履歷 Profile 之 3072 維度正規化向量
        query_vec = await asyncio.to_thread(self.embedding.embed_query, query_text)
        
        # 2. 向 2045 筆題庫進行向量相似度與學系混合比對
        matched_questions = self.repository.search_similar_questions_by_vector(
            query_vec=query_vec,
            department=major,
            top_k=top_k
        )
        return matched_questions

    def format_rag_context_seeds(self, questions: List[Dict[str, Any]]) -> str:
        """Formats retrieved sample questions and rubrics into a clean seed context string for LLM injection."""
        if not questions:
            return "（尚無比對到特定範例題目，請依據目標學系專業自由出題）"

        formatted_parts = []
        for idx, q in enumerate(questions, 1):
            q_text = q.get("question", "")
            q_cat = q.get("question_category", "通用型問題")
            q_diff = q.get("difficulty_level", "標準題")
            q_ref = q.get("reference_answer", "")
            
            part = (
                f"【範例種子 {idx}】(類別: {q_cat} | 難易度: {q_diff})\n"
                f"題目內文：{q_text}\n"
                f"擬答引導：{q_ref[:100]}...\n"
            )
            formatted_parts.append(part)

        return "\n".join(formatted_parts)

    async def generate_rag_question_for_candidate(
        self,
        candidate_profile: Union[str, CandidateProfile],
        target_school: Optional[str] = None,
        target_major: Optional[str] = None,
        interview_mode: str = "標準面試",
        transcript: str = "[系統]: 面試開始。"
    ) -> Dict[str, Any]:
        """End-to-End RAG Question Generation pipeline via Gemma-4-31B-it."""
        if isinstance(candidate_profile, CandidateProfile):
            profile_text = candidate_profile.to_structured_text()
            school = target_school or candidate_profile.target_school
            major = target_major or candidate_profile.target_major
        else:
            profile_text = str(candidate_profile)
            school = target_school or ""
            major = target_major or ""

        sample_qs = await self.retrieve_sample_questions_for_candidate(
            candidate_profile=candidate_profile,
            target_major=major,
            target_school=school,
            top_k=3
        )
        rag_seed_context = self.format_rag_context_seeds(sample_qs)

        generated_question = await gemma_client.invoke_with_system_prompt(
            prompt_name="question_generation",
            user_input="",
            target_school=school,
            target_major=major,
            interview_mode=interview_mode,
            candidate_profile=profile_text,
            sample_questions=rag_seed_context,
            transcript=transcript
        )

        return {
            "generated_question": generated_question,
            "rag_seed_questions": sample_qs,
            "rag_seed_context": rag_seed_context
        }

rag_service = RAGRetrieverService()
