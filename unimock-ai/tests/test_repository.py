import pytest
from app.repositories.question_repository import QuestionRepository

def test_question_repository_loading():
    repo = QuestionRepository()
    all_qs = repo.get_all_questions()
    assert len(all_qs) > 0
    assert "id" in all_qs[0]
    assert "question" in all_qs[0]

def test_question_repository_filtering():
    repo = QuestionRepository()
    qs = repo.get_questions_by_filter(department="資訊工程學系", limit=3)
    assert len(qs) > 0
    assert isinstance(qs, list)

def test_vector_similarity_search():
    repo = QuestionRepository()
    results = repo.search_similar_questions("請向非資工背景者解釋 Stack 與 Queue 差別", top_k=2)
    assert len(results) == 2
    assert "question" in results[0]

def test_get_by_id():
    repo = QuestionRepository()
    q = repo.get_question_id = repo.get_question_by_id("q_0001")
    assert q is not None
    assert q["id"] == "q_0001"
