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
from app.models.candidate_model import CandidateProfile

def test_candidate_profile_model_structured_text():
    """Verify CandidateProfile synthesizes all 8 core resume dimensions into structured text."""
    profile = CandidateProfile(
        target_school="國立台灣大學",
        target_major="資訊工程學系",
        target_group="資訊電機學群",
        autobiography="從小熱愛資訊科學與寫程式，熱衷於演算法探索與系統架構設計。",
        experiences=["高中資訊社社長", "校園資訊設備維護志工隊隊長"],
        academic_performance="班級排名 1/45 (前 2%)，APCS 實作題 4 級分",
        coursework=["高級程式設計預修", "AP 微積分 BC", "演算法初論"],
        club_leadership=["資訊研究社社長：舉辦全校性 Hackerathon 程式競賽"],
        projects_and_awards=["全國軟體競賽高中組一等獎", "智慧校園排課系統專案 (Python/FastAPI)"],
        thesis_and_research="高中小論文優等：以深度學習進行車牌自動辨識之研究",
        certifications_and_skills=["TOEIC 920", "APCS 觀念4級/實作4級", "Python", "C++", "Git"]
    )
    text = profile.to_structured_text()
    assert "國立台灣大學 資訊工程學系" in text
    assert "自傳摘要" in text
    assert "全國軟體競賽高中組一等獎" in text
    assert "APCS 觀念4級/實作4級" in text

def test_full_resume_candidate_profile_vectorization():
    """Verify full 8-dimension resume CandidateProfile vectorization produces 3072-dimensional vector."""
    profile = CandidateProfile(
        target_school="國立台灣大學",
        target_major="資訊工程學系",
        autobiography="從小熱愛資訊科學與寫程式",
        experiences=["高中資訊社社長"],
        academic_performance="班級排名 1/45",
        coursework=["高級程式設計預修"],
        club_leadership=["資訊研究社社長"],
        projects_and_awards=["全國軟體競賽高中組一等獎"],
        thesis_and_research="深度學習車牌辨識小論文",
        certifications_and_skills=["TOEIC 920", "Python"]
    )
    query_text = f"目標學系: {profile.target_major}。\n【全方位履歷歷程】\n{profile.to_structured_text()}"
    vec = embedding_service.embed_query(query_text)
    assert isinstance(vec, list)
    assert len(vec) == 3072

def test_rag_similarity_search_retrieval_with_candidate_profile():
    """Verify RAG similarity search retrieves relevant sample questions using CandidateProfile object."""
    async def _test():
        profile = CandidateProfile(
            target_school="國立台灣大學",
            target_major="資訊工程學系",
            projects_and_awards=["全國軟體競賽一等獎", "Stack與Queue網頁展演專案"],
            certifications_and_skills=["Python", "Data Structures"]
        )
        matched_qs = await rag_service.retrieve_sample_questions_for_candidate(
            candidate_profile=profile,
            top_k=3
        )
        assert isinstance(matched_qs, list)
        assert len(matched_qs) > 0
        print(f"\n[CandidateProfile RAG Retrieval Test] Top Question: {matched_qs[0].get('question')[:50]}")
    
    asyncio.run(_test())

def test_end_to_end_rag_question_generation_with_full_candidate_profile():
    """Test full end-to-end RAG retriever + Gemma 4 LLM Question Generation with CandidateProfile."""
    async def _test():
        profile = CandidateProfile(
            target_school="國立台灣大學",
            target_major="資訊工程學系",
            autobiography="熱愛演算法與資安研究",
            projects_and_awards=["全國軟體競賽一等獎"],
            thesis_and_research="基於Prepared Statements之SQL防禦小論文"
        )
        result = await rag_service.generate_rag_question_for_candidate(
            candidate_profile=profile,
            interview_mode="頂大嚴謹模式",
            transcript="[系統]: 面試開始。[考官]: 請用 1 分鐘自我介紹。"
        )
        assert "generated_question" in result
        assert "rag_seed_questions" in result
        assert len(result["generated_question"].strip()) > 0
        safe_q = result["generated_question"][:100].encode("ascii", "ignore").decode("ascii") or "Generated question OK"
        print(f"\n[End-to-End CandidateProfile RAG Generation Test]: {safe_q}")

    asyncio.run(_test())

if __name__ == "__main__":
    pytest.main(["-v", __file__])
