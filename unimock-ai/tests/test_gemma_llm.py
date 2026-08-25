import os
import pytest
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
from langchain_core.output_parsers import StrOutputParser

from app.services.gemma_llm import GemmaLLMClient, gemma_client
from app.config import settings

def test_gemma_llm_client_initialization():
    """Verify GemmaLLMClient instantiates with configured settings."""
    assert gemma_client._llm_type == "gemma-chat-client"
    assert gemma_client.model_name == settings.PRIMARY_LLM_MODEL
    assert gemma_client.fallback_model_name == settings.FALLBACK_LLM_MODEL

def test_chatml_formatting():
    """Verify messages convert cleanly to ChatML turn format."""
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
    assert formatted.endswith("<start_of_turn>model\n")

def test_langchain_chain_execution():
    """Test standard LangChain ChatPromptTemplate pipeline integration."""
    prompt = ChatPromptTemplate.from_messages([
        ("system", "你是一位親切的面試引導員。請用簡短一 village 句話回答。"),
        ("human", "請用一短句說出面試最重要的心態是什麼？")
    ])
    
    chain = prompt | gemma_client | StrOutputParser()
    response = chain.invoke({})
    
    assert isinstance(response, str)
    assert len(response.strip()) > 0
    print(f"\n[Gemma LLM Response Test] Generated Output: {response}")

if __name__ == "__main__":
    pytest.main(["-v", __file__])
