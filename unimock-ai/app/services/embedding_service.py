import os
import math
from typing import List
import google.generativeai as genai
from app.config import settings

class GeminiEmbeddingService:
    """
    Strict Service Wrapper for Google AI Studio Gemini Embedding 2 model (models/gemini-embedding-2).
    Calculates 3072-dimensional normalized dense vector representations without any fallback loops.
    """
    def __init__(self, model_name: str = "models/gemini-embedding-2"):
        self.model_name = model_name
        self.api_key = settings.GEMINI_API_KEY or os.environ.get("GEMINI_API_KEY", "")
        if self.api_key:
            genai.configure(api_key=self.api_key)

    def embed_query(self, text: str) -> List[float]:
        """
        Generate 3072-dimensional normalized embedding vector using strict models/gemini-embedding-2.
        Raises exception if API call fails (no silent fallback).
        """
        if not text or not text.strip():
            return [0.0] * 3072

        api_key = settings.GEMINI_API_KEY or os.environ.get("GEMINI_API_KEY", "")
        if not api_key:
            raise ValueError("GEMINI_API_KEY is not configured in unimock-ai/.env!")

        genai.configure(api_key=api_key)
        
        # Strict single call to models/gemini-embedding-2
        result = genai.embed_content(
            model=self.model_name,
            content=text
        )
        embedding = result.get("embedding", [])
        if not embedding:
            raise ValueError(f"Empty embedding returned from Google API for model {self.model_name}")
            
        return self._normalize(embedding)

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """Generate embedding vectors for a batch of documents."""
        return [self.embed_query(t) for t in texts]

    def _normalize(self, vec: List[float]) -> List[float]:
        norm = math.sqrt(sum(x * x for x in vec))
        if norm == 0:
            return vec
        return [x / norm for x in vec]

embedding_service = GeminiEmbeddingService()
