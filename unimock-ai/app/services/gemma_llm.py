import os
import re
import time
import asyncio
from typing import List, Dict, Any, Optional, AsyncGenerator
import google.generativeai as genai
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.messages import BaseMessage, HumanMessage, SystemMessage, AIMessage
from langchain_core.outputs import ChatResult, ChatGeneration
from pydantic import Field, PrivateAttr

from app.config import settings
from app.services.prompt_manager import prompt_manager
from app.services.security_guardrail import security_guardrail
from app.services.context_manager import token_context_guard

class GemmaLLMClient(BaseChatModel):
    """
    Unified Resilient LangChain ChatModel Client Interface strictly for Gemma-4-31B-it (models/gemma-4-31b-it).
    
    Day 9 Resilient Protection Mechanisms:
    1. 429 Rate Limit & Error Exponential Backoff Retry Loop (max_retries=3, parses 429 retry_delay).
    2. Token Count Estimator & Dynamic Context Truncation Guard (prevents Context Window Overflow).
    3. Async Streaming Output (`astream_with_system_prompt`) for real-time SSE token streaming.
    4. Privacy & Security Guardrail (blocks prompt injection while allowing academic security queries).
    """
    model_name: str = Field(default_factory=lambda: settings.PRIMARY_LLM_MODEL)
    temperature: float = Field(default_factory=lambda: settings.LLM_TEMPERATURE)
    top_p: float = Field(default_factory=lambda: settings.LLM_TOP_P)
    max_retries: int = Field(default=3)
    base_backoff_delay: float = Field(default=2.0)
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
        return "resilient-gemma-4-31b-client"

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

    def clean_markdown_formatting(self, text: str) -> str:
        """
        Removes remaining Markdown artifacts, prefix labels, bullet symbols,
        English prompt leaks (e.g. Language: Traditional Chinese), Alternative options, backticks, and surrounding quotes from LLM outputs.
        """
        if not text:
            return ""
        
        # 1. Remove XML/HTML tags and <think> blocks
        cleaned = re.sub(r'<think>.*?</think>', '', text, flags=re.DOTALL).strip()
        cleaned = re.sub(r'<[^>]+>', '', cleaned)

        # 2. Remove "Language: ...", "Ask a ...", "Alternative: ...", "(Clean and direct)", "Socratic questioning"
        cleaned = re.sub(r'(?i)Language\s*:\s*(?:Traditional\s*Chinese|Use\s*traditional\s*Chinese|Chinese)[\.\,\;]*\s*', '', cleaned)
        cleaned = re.sub(r'(?i)(Alternative|Option\s*[A-Z\d]?|Draft\s*\d?|Clean\s*and\s*direct|Socratic\s*questioning[^\.\,\n]*|Ask\s+a\s+[^\.\,\n]*)[\:\.\-]*\s*', '', cleaned)
        cleaned = re.sub(r'\([^)]*(?:Clean|direct|Socratic|Language)[^)]*\)', '', cleaned, flags=re.IGNORECASE)

        # 3. Extract last non-bullet line if LLM generated bullet points / draft notes
        lines = [l.strip() for l in cleaned.splitlines() if l.strip()]
        candidate_lines = []
        for l in lines:
            if re.match(r'^[\*\-\+\d\.]+\s*(Draft|Role|Situation|Task|Action|Result|Option|Alternative|Socratic|Language|分析|筆記|推理)', l, re.IGNORECASE):
                continue
            if l.startswith('* ') or l.startswith('- ') or l.startswith('+ '):
                continue
            candidate_lines.append(l)

        if candidate_lines:
            cleaned = candidate_lines[-1]
        elif lines:
            cleaned = lines[-1]

        # 4. Strip leading English clauses (e.g. "In the context of Fed rate hikes...") if followed by Chinese text
        english_lead_match = re.search(r'^(?:Language\s*:|In the context of|According to|Based on|Socratic|Regarding|Ask a)[^\n\u4e00-\u9fff]*[\,\:\.\-]?\s*(?=[\u4e00-\u9fff])', cleaned, re.IGNORECASE)
        if english_lead_match:
            cleaned = cleaned[english_lead_match.end():].strip()

        # 5. Strip all bracketed/parenthesized prefixes
        prefix_pattern = r'^(【[^】]+】|\[[^\]]+\]|\([^)]+\)|Alternative:|Option [A-Z]:|Option:|\w+:|問：|問題：|追問：|考官：|考官發問：|提問：)\s*'
        cleaned = re.sub(prefix_pattern, '', cleaned, flags=re.IGNORECASE).strip()
        cleaned = re.sub(prefix_pattern, '', cleaned, flags=re.IGNORECASE).strip()

        # 6. Remove markdown headings, asterisks, backticks, quotes
        cleaned = re.sub(r'^#+\s*', '', cleaned)
        cleaned = cleaned.replace('*', '').replace('`', '').replace('~', '')
        cleaned = cleaned.replace('"', '').replace("'", '')

        # 7. Strip leading/trailing quote marks
        cleaned = re.sub(r'^[「『"“\'`]\s*', '', cleaned)
        cleaned = re.sub(r'\s*[」』"”\'`]$', '', cleaned)

        return cleaned.strip()

    def _strip_thinking_blocks(self, text: str) -> str:
        """
        Strips Gemma chain-of-thought thinking blocks and applies clean_markdown_formatting.
        """
        if not text:
            return text
        return self.clean_markdown_formatting(text)

    def _generate(
        self,
        messages: List[BaseMessage],
        stop: Optional[List[str]] = None,
        run_manager: Optional[Any] = None,
        **kwargs: Any,
    ) -> ChatResult:
        """
        Executes generation using Gemma-4-31B-it with Exponential Backoff Retry Loop
        and 429 Rate Limit Protection.
        """
        api_key = self.api_key or settings.GEMINI_API_KEY or os.environ.get("GEMINI_API_KEY", "")
        if api_key:
            genai.configure(api_key=api_key)

        # 1. Check latest user input with security guardrail
        human_inputs = [msg.content for msg in messages if isinstance(msg, HumanMessage)]
        if human_inputs:
            latest_input = human_inputs[-1]
            is_safe, reason = security_guardrail.verify_input_safety(latest_input)
            if not is_safe:
                refusal_msg = AIMessage(content="[Security Alert] 系統檢測到不符合規範之提示詞覆蓋或指令擷取企圖，該請求已安全攔截。")
                return ChatResult(generations=[ChatGeneration(message=refusal_msg)])

        prompt_str = self._format_messages_to_gemma_chatml(messages)

        # 2. Resilient Exponential Backoff Retry Loop
        last_exception = None
        for attempt in range(self.max_retries):
            try:
                response = self._model.generate_content(prompt_str)
                output_text = response.text if response and hasattr(response, "text") else ""
                clean_text = re.sub(r"<end_of_turn>$", "", output_text).strip()
                # Strip Gemma chain-of-thought thinking blocks:
                # Gemma sometimes outputs reasoning as markdown bullets before the final answer.
                # The actual answer is always the last non-empty paragraph after thinking.
                clean_text = self._strip_thinking_blocks(clean_text)
                message = AIMessage(content=clean_text)
                return ChatResult(generations=[ChatGeneration(message=message)])
            except Exception as e:
                last_exception = e
                err_msg = str(e).lower()
                
                # Check for 429 Rate Limit / Quota Exceeded
                if "429" in err_msg or "resource_exhausted" in err_msg or "quota" in err_msg:
                    retry_delay = self.base_backoff_delay * (2 ** attempt) + 1.0
                    match = re.search(r'retry\s+in\s+([\d\.]+)\s*s', err_msg)
                    if match:
                        retry_delay = max(retry_delay, float(match.group(1)) + 2.0)
                    time.sleep(retry_delay)
                else:
                    time.sleep(self.base_backoff_delay * (attempt + 1))

        # Raise exception if all retries fail
        raise RuntimeError(f"Gemma LLM API call failed after {self.max_retries} attempts: {last_exception}")

    async def invoke_with_system_prompt(
        self,
        prompt_name: str,
        user_input: str = "",
        history: Optional[List[BaseMessage]] = None,
        **prompt_kwargs: Any
    ) -> str:
        """
        Asynchronously loads system prompt template, applies TokenContextGuard truncation,
        validates security guardrails, and executes resilient Gemma-4-31B LLM generation.
        """
        # Sanitize prompt kwargs to prevent Context Window Overflow
        clean_kwargs = token_context_guard.sanitize_prompt_kwargs(prompt_kwargs)
        
        system_prompt_text = await prompt_manager.get_system_prompt(prompt_name, **clean_kwargs)
        
        messages: List[BaseMessage] = [SystemMessage(content=system_prompt_text)]
        if history:
            messages.extend(history)
        
        if user_input and user_input.strip():
            messages.append(HumanMessage(content=user_input.strip()))

        result = await asyncio.to_thread(self._generate, messages)
        return result.generations[0].message.content

    async def astream_with_system_prompt(
        self,
        prompt_name: str,
        user_input: str = "",
        history: Optional[List[BaseMessage]] = None,
        **prompt_kwargs: Any
    ) -> AsyncGenerator[str, None]:
        """
        Asynchronously streams output tokens from Gemma-4-31B-it model for real-time SSE streaming.
        """
        clean_kwargs = token_context_guard.sanitize_prompt_kwargs(prompt_kwargs)
        system_prompt_text = await prompt_manager.get_system_prompt(prompt_name, **clean_kwargs)
        
        messages: List[BaseMessage] = [SystemMessage(content=system_prompt_text)]
        if history:
            messages.extend(history)
        if user_input and user_input.strip():
            messages.append(HumanMessage(content=user_input.strip()))

        if user_input and user_input.strip():
            is_safe, reason = security_guardrail.verify_input_safety(user_input.strip())
            if not is_safe:
                yield "[Security Alert] 系統檢測到不符合規範之提示詞覆蓋或指令擷取企圖，該請求已安全攔截。"
                return

        prompt_str = self._format_messages_to_gemma_chatml(messages)
        
        def _stream_sync():
            return self._model.generate_content(prompt_str, stream=True)

        response_stream = await asyncio.to_thread(_stream_sync)
        in_think_block = False
        think_buffer = ""
        for chunk in response_stream:
            if not chunk.text:
                continue
            text_chunk = chunk.text
            if "<think>" in text_chunk:
                in_think_block = True
            
            if in_think_block:
                think_buffer += text_chunk
                if "</think>" in think_buffer:
                    in_think_block = False
                    after_think = think_buffer.split("</think>", 1)[1].strip()
                    if after_think:
                        yield after_think
                    think_buffer = ""
                continue
            
            yield text_chunk
            await asyncio.sleep(0.01)

gemma_client = GemmaLLMClient()
