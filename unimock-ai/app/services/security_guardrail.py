import re
from typing import Tuple

class SecurityGuardrail:
    """
    Security and Privacy Guardrail for UniMock AI LLM Interface.
    
    Distinguishes strictly between:
    1. Malicious Prompt Injection / Jailbreak Attacks (System prompt leaking, instruction overrides) -> BLOCKED
    2. Legitimate Cybersecurity Academic / Technical Questions (SQL Injection defenses, TLS handshakes, etc.) -> ALLOWED
    """
    
    # Injection & Attack patterns targeting LLM prompt hijacking or credential theft
    ATTACK_PATTERNS = [
        r"ignore\s+(all\s+)?(previous|prior)\s+instructions",
        r"forget\s+(all\s+)?(previous|prior)\s+instructions",
        r"override\s+(system\s+)?prompt",
        r"reveal\s+(your\s+)?system\s+prompt",
        r"show\s+(me\s+)?(your\s+)?system\s+prompt",
        r"print\s+(your\s+)?api[_\s]?key",
        r"display\s+(your\s+)?credentials",
        r"you\s+are\s+now\s+in\s+(developer|dan)\s+mode",
        r"忽略(之前|先前)的(指令|設定|提示詞)",
        r"(印出|顯示|揭露)(你的)?(系統提示詞|System Prompt|API Key|密碼|密鑰)",
        r"(重置|覆蓋)(系統提示詞|你的角色)",
        r"進入(開發者模式|無限制模式)"
    ]

    # Legitimate cybersecurity context keywords (Academic/Technical Q&A)
    CYBERSECURITY_CONTEXT_KEYWORDS = [
        "sql injection", "xss", "csrf", "tls", "rsa", "firewall",
        "zero-day", "phishing", "encryption", "decryption",
        "資安", "資訊安全", "網路安全", "滲透測試", "社交工程",
        "防禦", "防範", "原理", "加密", "解密", "憑證", "修補"
    ]

    def verify_input_safety(self, user_input: str) -> Tuple[bool, str]:
        """
        Verifies user input for safety.
        Returns: (is_safe: bool, refusal_or_reason: str)
        """
        if not user_input or not user_input.strip():
            return True, ""

        clean_input = user_input.strip()

        # Check if input matches malicious prompt injection patterns
        for pattern in self.ATTACK_PATTERNS:
            if re.search(pattern, clean_input, re.IGNORECASE):
                # Double-check if it's a legitimate academic question asking about defense principles
                if self._is_legitimate_cybersecurity_question(clean_input):
                    return True, "Allowed: Recognized as legitimate cybersecurity academic query."
                
                return False, "Security Block: Prompt Injection or System Prompt Hijacking Attempt Detected."

        return True, "Safe input."

    def _is_legitimate_cybersecurity_question(self, text: str) -> bool:
        """
        Checks if text is a legitimate academic question about security defense or principles.
        """
        lower_text = text.lower()
        has_academic_intent = any(kw in lower_text for kw in ["原理", "防禦", "防範", "如何", "說明", "概念", "面試", "學科", "what is", "how to defend"])
        has_security_keyword = any(kw in lower_text for kw in self.CYBERSECURITY_CONTEXT_KEYWORDS)
        
        # Does NOT explicitly ask to output system prompts or secrets
        asks_for_secret = any(s in lower_text for s in ["system prompt", "api key", "密鑰", "密碼", "指令"])
        
        return has_academic_intent and has_security_keyword and not asks_for_secret

security_guardrail = SecurityGuardrail()
