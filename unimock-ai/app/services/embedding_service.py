import os
import math
from typing import List
import google.generativeai as genai
from app.config import settings

class GeminiEmbeddingService:
    """
    Service wrapper for Google AI Studio Gemini Embedding 2 model (models/gemini-embedding-2).
    Calculates normalized dense vector representations for interview questions and candidate answers.
    """
    def __init__(self, model_name: str = "models/gemini-embedding-2"):
        self.model_name = model_name
        self.api_key = settings.GEMINI_API_KEY or os.environ.get("GEMINI_API_KEY", "")
        if self.api_key:
            genai.configure(api_key=self.api_key)

    def embed_query(self, text: str) -> List[float]:
        """Generate embedding vector for search queries."""
        if not text or not text.strip():
            return [0.0] * 768

        if self.api_key:
            for model_try in [self.model_name, "models/gemini-embedding-2", "models/gemini-embedding-001"]:
                try:
                    result = genai.embed_content(
                        model=model_try,
                        content=text
                    )
                    embedding = result.get("embedding", [])
                    if embedding:
                        return self._normalize(embedding)
                except Exception as e:
                    # Print warning if API fails and fallback to next or pseudo-vector
                    continue

        return self._pseudo_embedding(text)

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """Generate embedding vectors for a batch of documents."""
        return [self.embed_query(t) for t in texts]

    def _normalize(self, vec: List[float]) -> List[float]:
        norm = math.sqrt(sum(x * x for x in vec))
        if norm == 0:
            return vec
        return [x / norm for x in vec]

    def _pseudo_embedding(self, text: str) -> List[float]:
        """Fallback deterministic pseudo-vector when offline or API key is not present."""
        vec = [0.0] * 768
        for i, char in enumerate(text):
            idx = (ord(char) * (i + 1)) % 768
            vec[idx] += 1.0
        return self._normalize(vec)

embedding_service = GeminiEmbeddingService()
