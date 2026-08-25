import os
import re
import asyncio
from typing import List, Dict, Any, Optional
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
    Unified LangChain ChatModel Client Interface strictly for Gemma-4-31B-it (models/gemma-4-31b-it).
    
    Architectural Standards:
    1. Dedicated Gemma 4 LLM: Exclusively utilizes `models/gemma-4-31b-it` for all LLM generations.
    2. Async System Prompt Loading: Dynamically loads system prompt templates from `docs/system_prompts/`.
    3. Privacy & Security Guardrail: Blocks prompt injection / system prompt leaking attacks, 
       while safely ALLOWING legitimate cybersecurity technical / academic interview questions.
    """
    model_name: str = Field(default_factory=lambda: settings.PRIMARY_LLM_MODEL)
    temperature: float = Field(default_factory=lambda: settings.LLM_TEMPERATURE)
    top_p: float = Field(default_factory=lambda: settings.LLM_TOP_P)
    api_key: Optional[str] = Field(default=None)

    _model: Any = PrivateAttr()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        effective_key = self.api_key or settings.GEMINI_API_KEY or os.environ.get("GEMINI_API_KEY", "")
        if effective_key:
            genai.configure(api_key=effective_key)
        
        self._model = genai.GenerativeModel(
            model_name=self.model_name,
            generation_config=genai.types.GenerationConfig(
                temperature=self.temperature,
                top_p=self.top_p
            )
        )

    @property
    def _llm_type(self) -> str:
        return "gemma-4-31b-client"

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
        """Executes generation using strict Gemma-4-31B-it model with security guardrails."""
        api_key = self.api_key or settings.GEMINI_API_KEY or os.environ.get("GEMINI_API_KEY", "")
        if api_key:
            genai.configure(api_key=api_key)

        # Check latest user input with security guardrail
        human_inputs = [msg.content for msg in messages if isinstance(msg, HumanMessage)]
        if human_inputs:
            latest_input = human_inputs[-1]
            is_safe, reason = security_guardrail.verify_input_safety(latest_input)
            if not is_safe:
                refusal_msg = AIMessage(content="[Security Alert] 系統檢測到不符合規範之提示詞覆蓋或指令擷取企圖，該請求已安全攔截。")
                return ChatResult(generations=[ChatGeneration(message=refusal_msg)])

        prompt_str = self._format_messages_to_gemma_chatml(messages)

        response = self._model.generate_content(prompt_str)
        output_text = response.text if response and hasattr(response, "text") else ""

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
        validates security guardrails, and executes strict Gemma-4-31B LLM generation.
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
