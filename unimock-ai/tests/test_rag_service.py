import os
import sys
import pytest
import asyncio

# Reconfigure stdout for Windows console UTF-8 support
if sys.stdout and hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

from app.services.rag_service import rag_service, RAGRetrieverService
from app.services.embedding_service import embedding_service
from app.repositories.question_repository import question_repository

def test_candidate_profile_vectorization():
    """Verify Candidate Profile vectorization produces 3072-dimensional vector."""
    candidate_profile = "高中數理資優班，曾獲得全國資訊競賽一等獎，精通 Python 與資料結構"
    query_text = f"目標學系: 資訊工程學系。個人經歷簡歷: {candidate_profile}"
    
    vec = embedding_service.embed_query(query_text)
    assert isinstance(vec, list)
    assert len(vec) == 3072

def test_rag_similarity_search_retrieval():
    """Verify RAG similarity search retrieves relevant sample questions matching target department."""
    async def _test():
        candidate_profile = "高中數理資優班，曾獲得全國資訊競賽一等獎，精通 Python 與資料結構"
        matched_qs = await rag_service.retrieve_sample_questions_for_candidate(
            candidate_profile=candidate_profile,
            target_major="資訊工程學系",
            top_k=3
        )
        assert isinstance(matched_qs, list)
        assert len(matched_qs) > 0
        print(f"\n[RAG Retrieval Test] Retracted Top Question: {matched_qs[0].get('question')[:50]}")
    
    asyncio.run(_test())

def test_rag_seed_context_formatting():
    """Verify formatting RAG questions into seed context for LLM injection."""
    sample_questions = [
        {
            "question": "請向非資訊背景的人解釋什麼是 Stack 與 Queue？",
            "question_category": "技術專業型問題",
            "difficulty_level": "進階專業題",
            "reference_answer": "Stack 採用 LIFO 概念..."
        }
    ]
    formatted = rag_service.format_rag_context_seeds(sample_questions)
    assert "【範例種子 1】" in formatted
    assert "請向非資訊背景的人解釋什麼是 Stack 與 Queue？" in formatted

def test_end_to_end_rag_question_generation():
    """Test full end-to-end RAG retriever + Gemma LLM Question Generation pipeline."""
    async def _test():
        result = await rag_service.generate_rag_question_for_candidate(
            candidate_profile="高中代表隊參加全國軟體競賽一等獎，熟悉 Python、Data Structures",
            target_school="國立台灣大學",
            target_major="資訊工程學系",
            interview_mode="頂大嚴謹模式",
            transcript="[系統]: 面試開始。[考官]: 請用 1 分鐘自我介紹。"
        )
        assert "generated_question" in result
        assert "rag_seed_questions" in result
        assert len(result["generated_question"].strip()) > 0
        safe_q = result["generated_question"][:100].encode("ascii", "ignore").decode("ascii") or "Generated question OK"
        print(f"\n[End-to-End RAG Generation Test]: {safe_q}")

    asyncio.run(_test())

if __name__ == "__main__":
    pytest.main(["-v", __file__])
