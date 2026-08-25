import os
import google.generativeai as genai
from app.config import settings

api_key = settings.GEMINI_API_KEY or os.environ.get("GEMINI_API_KEY", "")
print(f"Testing GEMINI_API_KEY: {api_key[:10]}...{api_key[-4:]}")

genai.configure(api_key=api_key)

models_to_test = [
    "models/gemini-embedding-2",
    "models/gemini-embedding-001",
    "models/gemini-embedding-2-preview"
]

for m in models_to_test:
    print(f"\n--- Testing model: {m} ---")
    try:
        res = genai.embed_content(
            model=m,
            content="測試模擬面試問題向量化"
        )
        emb = res.get("embedding", [])
        print(f"SUCCESS for {m}! Received embedding vector of dimension: {len(emb)}")
        print(f"Sample values (first 5): {emb[:5]}")
        break
    except Exception as e:
        print(f"FAILED for model {m}: {type(e).__name__}: {e}")
