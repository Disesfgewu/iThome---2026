import os
import re
import asyncio
from typing import List, Dict, Any, Optional, Union
import google.generativeai as genai
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.messages import BaseMessage, HumanMessage, SystemMessage, AIMessage
from langchain_core.outputs import ChatResult, ChatGeneration
from pydantic import Field, PrivateAttr

from app.config import settings
from app.services.prompt_manager import prompt_manager
from app.services.security_guardrail import security_guardrail

class GemmaLLMClient(BaseChatModel):
    """
    Unified LangChain ChatModel Client Interface for Gemma 4 LLM (models/gemma-4-31b-it).
    
    Architectural Enhancements:
    1. Async System Prompt Loading: Dynamically loads system prompt templates from `docs/system_prompts/`.
    2. Empty User Input Default: User input is empty by default until populated by candidate responses.
    3. Privacy & Security Guardrail: Blocks prompt injection / system prompt leaking attacks, 
       while safely ALLOWING legitimate cybersecurity technical / academic interview questions.
    4. Auto Fallback: Retries with `models/gemini-2.5-flash` if primary Gemma model hits limits.
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
        """Formats LangChain message sequence into ChatML / Gemma turn format."""
        formatted_parts = []
        for msg in messages:
            if isinstance(msg, SystemMessage):
                formatted_parts.append(f"<start_of_turn>system\n{msg.content.strip()}<end_of_turn>")
            elif isinstance(msg, HumanMessage):
                if msg.content and msg.content.strip():
                    formatted_parts.append(f"<start_of_turn>user\n{msg.content.strip()}<end_of_turn>")
            elif isinstance(msg, AIMessage):
                formatted_parts.append(f"<start_of_turn>model\n{msg.content.strip()}<end_of_turn>")
            else:
                if msg.content and msg.content.strip():
                    formatted_parts.append(f"<start_of_turn>user\n{msg.content.strip()}<end_of_turn>")
        
        formatted_parts.append("<start_of_turn>model\n")
        return "\n".join(formatted_parts)

    def _generate(
        self,
        messages: List[BaseMessage],
        stop: Optional[List[str]] = None,
        run_manager: Optional[Any] = None,
        **kwargs: Any,
    ) -> ChatResult:
        """Executes generation with security guardrail verification and fallback."""
        api_key = self.api_key or settings.GEMINI_API_KEY or os.environ.get("GEMINI_API_KEY", "")
        if api_key:
            genai.configure(api_key=api_key)

        # Check latest user message for security & privacy guardrails
        human_inputs = [msg.content for msg in messages if isinstance(msg, HumanMessage)]
        if human_inputs:
            latest_input = human_inputs[-1]
            is_safe, reason = security_guardrail.verify_input_safety(latest_input)
            if not is_safe:
                refusal_msg = AIMessage(content="[Security Alert] 系統檢測到不符合規範之提示詞覆蓋或指令擷取企圖，該請求已安全攔截。")
                return ChatResult(generations=[ChatGeneration(message=refusal_msg)])

        prompt_str = self._format_messages_to_gemma_chatml(messages)

        try:
            response = self._primary_model.generate_content(prompt_str)
            output_text = response.text if response and hasattr(response, "text") else ""
        except Exception as primary_err:
            print(f"[Gemma LLM Warning] Primary model ({self.model_name}) error: {primary_err}. Falling back to {self.fallback_model_name}...")
            try:
                response = self._fallback_model.generate_content(prompt_str)
                output_text = response.text if response and hasattr(response, "text") else ""
            except Exception as fallback_err:
                raise RuntimeError(f"Gemma Chat Client failed on both primary and fallback models. Error: {fallback_err}")

        clean_text = re.sub(r"<end_of_turn>$", "", output_text).strip()
        message = AIMessage(content=clean_text)
        return ChatResult(generations=[ChatGeneration(message=message)])

    async def invoke_with_system_prompt(
        self,
        prompt_name: str,
        user_input: str = "",
        history: Optional[List[BaseMessage]] = None,
        **prompt_kwargs: Any
    ) -> str:
        """
        Asynchronously loads system prompt template from `docs/system_prompts/`,
        validates security guardrails, and executes LLM generation.
        
        - user_input is empty string by default.
        - System prompts are loaded asynchronously.
        """
        system_prompt_text = await prompt_manager.get_system_prompt(prompt_name, **prompt_kwargs)
        
        messages: List[BaseMessage] = [SystemMessage(content=system_prompt_text)]
        if history:
            messages.extend(history)
        
        if user_input and user_input.strip():
            messages.append(HumanMessage(content=user_input.strip()))

        result = await asyncio.to_thread(self._generate, messages)
        return result.generations[0].message.content

gemma_client = GemmaLLMClient()
