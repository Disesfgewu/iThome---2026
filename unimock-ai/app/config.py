import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "UniMock AI"
    VERSION: str = "1.0.0"
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
    
    # LLM Settings for Gemma / Gemini
    PRIMARY_LLM_MODEL: str = os.getenv("PRIMARY_LLM_MODEL", "models/gemma-4-31b-it")
    FALLBACK_LLM_MODEL: str = os.getenv("FALLBACK_LLM_MODEL", "models/gemini-2.5-flash")
    LLM_TEMPERATURE: float = float(os.getenv("LLM_TEMPERATURE", "0.7"))
    LLM_TOP_P: float = float(os.getenv("LLM_TOP_P", "0.9"))
    
    class Config:
        env_file = ".env"
        extra = "ignore"

settings = Settings()
