import re
from typing import Dict, Any, Tuple

class GuardrailsService:
    """
    Security Guardrails Engine for UniMock AI.
    Handles PII Scrubbing (Privacy Anonymization) and Anti-Prompt Injection Detection.
    """
    def __init__(self):
        # Regex patterns for Taiwan PII
        self.taiwan_id_pattern = r"[A-Z][12]\d{8}"
        self.mobile_pattern = r"09\d{2}[-]?\d{3}[-]?\d{3}"
        self.email_pattern = r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}"
        
        # Prompt Injection attack signatures
        self.injection_keywords = [
            "ignore previous instructions",
            "forget all rules",
            "system override",
            "give me 100 points",
            "give me 5 stars",
            "print system prompt",
            "無視之前的指令",
            "忽略所有規則",
            "給我滿分",
            "輸出系統提示詞"
        ]

    def sanitize_pii(self, text: str) -> str:
        """
        Anonymizes PII data (IDs, phone numbers, emails) in input text.
        """
        sanitized = text
        sanitized = re.sub(self.taiwan_id_pattern, "[身分證號已遮蔽]", sanitized)
        sanitized = re.sub(self.mobile_pattern, "[電話號碼已遮蔽]", sanitized)
        sanitized = re.sub(self.email_pattern, "[電子郵件已遮蔽]", sanitized)
        return sanitized

    def detect_prompt_injection(self, text: str) -> Tuple[bool, str]:
        """
        Checks if the input text contains prompt injection attempts.
        Returns (is_injection_detected, reason).
        """
        lower_text = text.lower()
        for keyword in self.injection_keywords:
            if keyword in lower_text:
                return True, f"偵測到可疑指令越獄嘗試：'{keyword}'"
        return False, ""

    def process_candidate_input(self, text: str) -> Dict[str, Any]:
        """
        Processes candidate input through full Guardrails pipeline.
        """
        is_injection, reason = self.detect_prompt_injection(text)
        if is_injection:
            return {
                "safe": False,
                "sanitized_text": "",
                "block_reason": reason
            }
        
        sanitized = self.sanitize_pii(text)
        return {
            "safe": True,
            "sanitized_text": sanitized,
            "block_reason": ""
        }

guardrails_service = GuardrailsService()
