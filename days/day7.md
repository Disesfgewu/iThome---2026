# 【Day 7】大腦就緒：LangChain 環境配置與 Gemma-4-31B 模型統一客戶端封裝

在完成了 Day 6 的題庫去識別化清洗與 Gemini Embedding 2 向量化整合後，今天我們進入核心 AI 大腦的搭建——**LangChain 生態系整合與 Gemma-4-31B 統一 Chat Client 客戶端封裝**。

我們將為 **Gemma-4-31B-it** 建立統一的 LangChain 介面，並針對 Gemma 特有的提示語法（ChatML Style Turn Tokens）進行自動化適配與雙模型備援（Fallback）。

---

## 1. Gemma 專屬 ChatML 提示詞結構設計 (Turn-based Prompting)

Gemma 系列 LLM 模型採用特有的 Turn-based `<start_of_turn>` 與 `<end_of_turn>` 標籤。我們透過 LangChain `ChatPromptTemplate` 進行結構化封裝：

```python
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

def build_interviewer_prompt():
    system_prompt = """你是一位親切但嚴謹的 {target_major} 大學面試主考官教授。
你的任務是根據學生的備審經歷進行面試發問。
回答風格請保持專業、鼓勵性，並針對技術與經歷細節進行適度深挖。
"""
    return ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        MessagesPlaceholder(variable_name="history"),
        ("human", "{user_input}")
    ])
```

---

## 2. 封裝統一 LangChain Gemma ChatModel 客戶端 (`app/services/gemma_llm.py`)

為了確保 Gemma 模型能無縫融入 LangChain Pipeline 管道（如 `ChatPromptTemplate | gemma_client | StrOutputParser()`），我們繼承 `BaseChatModel` 實作了統一的客戶端：

- **主模型指定：** `models/gemma-4-31b-it`（Google AI Studio 託管之 31B 旗艦模型）。
- **自動降級備援 (Auto Fallback)：** 當主模型遇到高負載或配額限制時，自動切換至 `models/gemini-2.5-flash`，確保面試流程永不中斷。
- **ChatML 自動轉譯：** 將 LangChain 訊息列自動轉換為 `<start_of_turn>system` / `user` / `model` 格式。

```python
import os
import re
from typing import List, Dict, Any, Optional
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
        """Formats LangChain message sequence into ChatML / Gemma turn format."""
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
        
        formatted_parts.append("<start_of_turn>model\n")
        return "\n".join(formatted_parts)

    def _generate(
        self,
        messages: List[BaseMessage],
        stop: Optional[List[str]] = None,
        run_manager: Optional[Any] = None,
        **kwargs: Any,
    ) -> ChatResult:
        """Executes generation using primary Gemma model, automatically falling back if needed."""
        api_key = self.api_key or settings.GEMINI_API_KEY or os.environ.get("GEMINI_API_KEY", "")
        if api_key:
            genai.configure(api_key=api_key)

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
                raise RuntimeError(f"Gemma Chat Client failed on both models. Error: {fallback_err}")

        clean_text = re.sub(r"<end_of_turn>$", "", output_text).strip()
        message = AIMessage(content=clean_text)
        return ChatResult(generations=[ChatGeneration(message=message)])

gemma_client = GemmaLLMClient()
```

---

## 3. Pytest 單元與整合測試驗證 (`tests/test_gemma_llm.py`)

我們撰寫了完整的 Pytest 測試套件，驗證 Gemma LLM 客戶端初始化、ChatML 語法轉譯與 LangChain 鏈式調用：

```python
import pytest
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
from langchain_core.output_parsers import StrOutputParser

from app.services.gemma_llm import GemmaLLMClient, gemma_client
from app.config import settings

def test_gemma_llm_client_initialization():
    assert gemma_client._llm_type == "gemma-chat-client"
    assert gemma_client.model_name == settings.PRIMARY_LLM_MODEL
    assert gemma_client.fallback_model_name == settings.FALLBACK_LLM_MODEL

def test_chatml_formatting():
    client = GemmaLLMClient()
    messages = [
        SystemMessage(content="你是一位嚴謹的資訊工程學系教授。"),
        HumanMessage(content="教授好，我申請貴系是因為想深入研究人工智慧。"),
        AIMessage(content="很好，那請告訴我你對機器學習中監督式學習的理解？")
    ]
    formatted = client._format_messages_to_gemma_chatml(messages)
    
    assert "<start_of_turn>system\n你是一位嚴謹的資訊工程學系教授。<end_of_turn>" in formatted
    assert "<start_of_turn>user\n教授好，我申請貴系是因為想深入研究人工智慧。<end_of_turn>" in formatted
    assert "<start_of_turn>model\n很好，那請告訴我你對機器學習中監督式學習的理解？<end_of_turn>" in formatted

def test_langchain_chain_execution():
    prompt = ChatPromptTemplate.from_messages([
        ("system", "你是一位親切的面試引導員。請用簡短一短句回答。"),
        ("human", "請用一短句說出面試最重要的心態是什麼？")
    ])
    chain = prompt | gemma_client | StrOutputParser()
    response = chain.invoke({})
    assert isinstance(response, str)
    assert len(response.strip()) > 0
```

### 測試執行結果

在 `unimock-ai/` 目錄執行測試：

```bash
$env:PYTHONPATH="."; .\venv\Scripts\python -m pytest tests/test_gemma_llm.py -v
```

測試輸出：
```text
tests/test_gemma_llm.py::test_gemma_llm_client_initialization PASSED [ 33%]
tests/test_gemma_llm.py::test_chatml_formatting PASSED            [ 66%]
tests/test_gemma_llm.py::test_langchain_chain_execution PASSED     [100%]

======================= 3 passed in 14.56s =======================
```

---

## 結語與明天預告

今天我們順利完成了 Gemma-4-31B 模型 Client 端的封裝、LangChain 生態系對接、ChatML 語法自動相容與雙模型自動降級備援機制。

明天 **【Day 8】**，我們將整合 RAG 檢索器與向量資料庫，讓 Gemma 能在發問時即時參考科系考古題並進行動態生成！
