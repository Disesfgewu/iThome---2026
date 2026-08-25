from typing import Dict, Any, List, Optional
from langchain_core.messages import HumanMessage, AIMessage, BaseMessage

class LangChainMemoryManager:
    """
    LangChain Multi-Turn Dialogue Memory Manager.
    Manages session-based conversation history using LangChain message abstractions
    and implements sliding token window buffer trimming to preserve dialogue context.
    """
    def __init__(self, max_token_limit: int = 2048):
        self.max_token_limit = max_token_limit
        self._memories: Dict[str, List[BaseMessage]] = {}

    def get_or_create_messages(self, session_id: str) -> List[BaseMessage]:
        """Retrieves or initializes message history list for a given session."""
        if session_id not in self._memories:
            self._memories[session_id] = []
        return self._memories[session_id]

    def add_user_message(self, session_id: str, message: str):
        """Appends user HumanMessage to session memory."""
        msgs = self.get_or_create_messages(session_id)
        msgs.append(HumanMessage(content=message))
        self._trim_messages(session_id)

    def add_ai_message(self, session_id: str, message: str):
        """Appends AI interviewer AIMessage to session memory."""
        msgs = self.get_or_create_messages(session_id)
        msgs.append(AIMessage(content=message))
        self._trim_messages(session_id)

    def _trim_messages(self, session_id: str):
        """Trims older messages when total estimated character/token length exceeds max_token_limit."""
        msgs = self.get_or_create_messages(session_id)
        max_chars = self.max_token_limit * 2
        while len(msgs) > 2 and sum(len(m.content) for m in msgs) > max_chars:
            msgs.pop(0)

    def get_buffer_string(self, session_id: str) -> str:
        """Formats LangChain messages into clean dialogue context string."""
        msgs = self.get_or_create_messages(session_id)
        formatted = []
        for msg in msgs:
            prefix = "[考官]" if isinstance(msg, AIMessage) else "[學生]"
            formatted.append(f"{prefix}: {msg.content}")
        return "\n".join(formatted)

    def clear_memory(self, session_id: str):
        """Clears session memory."""
        if session_id in self._memories:
            del self._memories[session_id]

memory_manager = LangChainMemoryManager(max_token_limit=2048)
