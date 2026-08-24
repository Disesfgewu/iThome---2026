# 【Day 7】大腦就緒：LangChain 環境配置與 Gemma 模型客製化串接

今天我們要將 Google AI Studio 的 **Gemma-4-31B-it** 模型深度整合進 **LangChain** 生態系中，並針對 Gemma 特有的提示語法（ChatML Style）進行適配。

---

## 1. Gemma 專屬 Prompt Template 設計

Gemma 模型對於 `<start_of_turn>` 與 `<end_of_turn>` 標籤十分敏感。我們透過 LangChain `ChatPromptTemplate` 進行結構化封裝：

```python
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

def build_interviewer_prompt():
    system_prompt = """你是一位親切但嚴謹的 {target_major} 大學教授。
你的任務是根據學生的備審經歷進行面試發問。
回答風格請保持專業、鼓勵性，並針對技術細節進行適度深挖。
"""
    return ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        MessagesPlaceholder(variable_name="history"),
        ("human", "{user_input}")
    ])
```

---

## 2. 封裝 Gemma ChatModel 客戶端 (`app/services/gemma_llm.py`)

```python
from langchain_community.chat_models import ChatGoogleGenerativeAI
from app.config import settings

def get_gemma_model():
    return ChatGoogleGenerativeAI(
        model=settings.DEFAULT_MODEL_NAME,
        google_api_key=settings.GEMINI_API_KEY,
        temperature=0.7,
        top_p=0.9
    )
```

---

## 結語與明天預告

今天我們建立了 LangChain 專用的 Gemma 模型介面與提示詞樣板。

明天 **【Day 8】**，我們將整合 RAG 檢索器與向量資料庫，讓 Gemma 能在發問時即時參考科系考古題！
