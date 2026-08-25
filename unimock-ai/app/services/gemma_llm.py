import os
import re
from typing import List, Dict, Any, Optional, Union
import google.generativeai as genai
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.messages import BaseMessage, HumanMessage, SystemMessage, AIMessage
from langchain_core.outputs import ChatResult, ChatGeneration
from pydantic import Field, PrivateAttr

from app.config import settings

class GemmaLLMClient(BaseChatModel):
    """
    Unified LangChain ChatModel Client Interface for Gemma 4 LLM (models/gemma-4-31b-it).
    
    Features:
    - Compatible with LangChain Runnable chains (ChatPromptTemplate | gemma_client | StrOutputParser).
    - Adaptable to ChatML / Gemma special turn tokens (<start_of_turn> / <end_of_turn>).
    - Robust Automatic Fallback: If primary model (gemma-4-31b-it) hits quota limits, 
      seamlessly retries with fallback model (gemini-2.5-flash).
    """
    model_name: str = Field(default_factory=lambda: settings.PRIMARY_LLM_MODEL)
    fallback_model_name: str = Field(default_factory=lambda: settings.FALLBACK_LLM_MODEL)
    temperature: float = Field(default_factory=lambda: settings.LLM_TEMPERATURE)
    top_p: float = Field(default_factory=lambda: settings.LLM_TOP_P)
    api_key: Optional[str] = Field(default=None)

    _primary_model: Any = PrivateAttr()
    _fallback_model: Any = PrivateAttr()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        effective_key = self.api_key or settings.GEMINI_API_KEY or os.environ.get("GEMINI_API_KEY", "")
        if effective_key:
            genai.configure(api_key=effective_key)
        
        self._primary_model = genai.GenerativeModel(
            model_name=self.model_name,
            generation_config=genai.types.GenerationConfig(
                temperature=self.temperature,
                top_p=self.top_p
            )
        )
        self._fallback_model = genai.GenerativeModel(
            model_name=self.fallback_model_name,
            generation_config=genai.types.GenerationConfig(
                temperature=self.temperature,
                top_p=self.top_p
            )
        )

    @property
    def _llm_type(self) -> str:
        return "gemma-chat-client"

    def _format_messages_to_gemma_chatml(self, messages: List[BaseMessage]) -> str:
        """
        Formats LangChain message sequence into ChatML / Gemma turn format:
        <start_of_turn>system ... <end_of_turn>
        <start_of_turn>user ... <end_of_turn>
        <start_of_turn>model ... <end_of_turn>
        """
        formatted_parts = []
        for msg in messages:
            if isinstance(msg, SystemMessage):
                formatted_parts.append(f"<start_of_turn>system\n{msg.content.strip()}<end_of_turn>")
            elif isinstance(msg, HumanMessage):
                formatted_parts.append(f"<start_of_turn>user\n{msg.content.strip()}<end_of_turn>")
            elif isinstance(msg, AIMessage):
                formatted_parts.append(f"<start_of_turn>model\n{msg.content.strip()}<end_of_turn>")
            else:
                formatted_parts.append(f"<start_of_turn>user\n{msg.content.strip()}<end_of_turn>")
        
        # Append turn prompt for model generation
        formatted_parts.append("<start_of_turn>model\n")
        return "\n".join(formatted_parts)

    def _generate(
        self,
        messages: List[BaseMessage],
        stop: Optional[List[str]] = None,
        run_manager: Optional[Any] = None,
        **kwargs: Any,
    ) -> ChatResult:
        """
        Executes generation using primary Gemma model, automatically falling back if quota/API error occurs.
        """
        api_key = self.api_key or settings.GEMINI_API_KEY or os.environ.get("GEMINI_API_KEY", "")
        if api_key:
            genai.configure(api_key=api_key)

        prompt_str = self._format_messages_to_gemma_chatml(messages)

        try:
            response = self._primary_model.generate_content(prompt_str)
            output_text = response.text if response and hasattr(response, "text") else ""
        except Exception as primary_err:
            # Fallback to secondary model if primary model fails or hits quota
            print(f"[Gemma LLM Warning] Primary model ({self.model_name}) error: {primary_err}. Falling back to {self.fallback_model_name}...")
            try:
                response = self._fallback_model.generate_content(prompt_str)
                output_text = response.text if response and hasattr(response, "text") else ""
            except Exception as fallback_err:
                raise RuntimeError(f"Gemma Chat Client failed on both primary and fallback models. Error: {fallback_err}")

        # Clean trailing Gemma turn tags if generated in output
        clean_text = re.sub(r"<end_of_turn>$", "", output_text).strip()
        
        message = AIMessage(content=clean_text)
        generation = ChatGeneration(message=message)
        return ChatResult(generations=[generation])

# Global instance for easy import and reuse
gemma_client = GemmaLLMClient()
