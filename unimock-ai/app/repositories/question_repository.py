import json
import os
from typing import List, Dict, Any, Optional
from app.services.embedding_service import embedding_service

class QuestionRepository:
    """
    De-identified Unified Question Repository with Pre-embedded Vector Support.
    Queries are scoped by Department Group, Department, Question Category, and Difficulty Level.
    Vector similarity search uses pre-embedded 768-dimensional vectors stored in the JSON DB.
    """
    def __init__(self, db_path: Optional[str] = None):
        if db_path is None:
            db_path = os.path.join(os.path.dirname(__file__), "..", "db", "interview_questions_db.json")
        self.db_path = os.path.abspath(db_path)
        self._questions: List[Dict[str, Any]] = []
        self.load_database()

    def load_database(self) -> None:
        """Loads de-identified questions from JSON storage safely."""
        if os.path.exists(self.db_path):
            with open(self.db_path, "r", encoding="utf-8") as f:
                self._questions = json.load(f)
        else:
            self._questions = []

    def save_database(self) -> None:
        """Persists question bank to JSON storage safely."""
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        with open(self.db_path, "w", encoding="utf-8") as f:
            json.dump(self._questions, f, ensure_ascii=False, indent=2)

    def get_all_questions(self) -> List[Dict[str, Any]]:
        """Returns a read-only copy of all de-identified questions."""
        return list(self._questions)

    def get_question_by_id(self, question_id: str) -> Optional[Dict[str, Any]]:
        """Finds a question by its unique ID."""
        for q in self._questions:
            if q.get("id") == question_id:
                return dict(q)
        return None

    def get_questions_by_filter(
        self,
        department_group: Optional[str] = None,
        department: Optional[str] = None,
        question_category: Optional[str] = None,
        difficulty_level: Optional[str] = None,
        limit: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Retrieves matching de-identified interview questions filtered by group, department, category, and difficulty.
        """
        matched = []
        for q in self._questions:
            if department and department.strip():
                if department not in q.get("department", "") and "通用" not in q.get("department", ""):
                    continue

            if department_group and department_group.strip():
                if department_group not in q.get("department_group", ""):
                    continue

            if question_category and question_category.strip():
                if q.get("question_category") != question_category:
                    continue

            if difficulty_level and difficulty_level.strip():
                if q.get("difficulty_level") != difficulty_level:
                    continue

            matched.append(dict(q))
            if len(matched) >= limit:
                break

        # Fallback if specific combination returns empty results
        if not matched:
            matched = [dict(q) for q in self._questions[:limit]]

        return matched

    def search_similar_questions(self, query_text: str, top_k: int = 3) -> List[Dict[str, Any]]:
        """
        Uses Gemini Embedding 2 model for query vector calculation (1 API call),
        then performs instant dot product / cosine similarity against pre-embedded vectors in DB!
        """
        if not query_text or not self._questions:
            return [dict(q) for q in self._questions[:top_k]]

        query_vec = embedding_service.embed_query(query_text)

        scored_questions = []
        for q in self._questions:
            # Use pre-stored embedding if available; fallback to live calculation if not yet pre-embedded
            doc_vec = q.get("embedding")
            if not doc_vec:
                doc_vec = embedding_service.embed_query(q.get("question", ""))

            dot_product = sum(a * b for a, b in zip(query_vec, doc_vec))
            scored_questions.append((dot_product, dict(q)))

        scored_questions.sort(key=lambda x: x[0], reverse=True)
        return [q for score, q in scored_questions[:top_k]]

    def add_question(self, question_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Safely adds a new de-identified question to the repository and calculates pre-embedding vector.
        """
        new_id = f"q_{len(self._questions) + 1:04d}"
        question_data["id"] = new_id
        question_data["deidentified"] = True
        
        # Pre-embed new question text
        if "embedding" not in question_data:
            question_data["embedding"] = embedding_service.embed_query(question_data.get("question", ""))
            
        self._questions.append(question_data)
        self.save_database()
        return dict(question_data)

question_repository = QuestionRepository()
