import re
from typing import Dict, Any, List

class TokenContextGuard:
    """
    Token Count Estimator & Dynamic Context Window Truncation Guard.
    
    Protects LLM calls against:
    1. 'Too Many Tokens Input' / Context Window Overflow.
    2. Excessive API cost / rate limit consumption.
    
    Strategies:
    - Token Estimation: Standard CJK character + word token estimation (~1.5 chars per token for CJK).
    - Smart Transcript Truncation: Keeps System Prompts intact while sliding-window truncating older turns in `{transcript}`.
    """
    def __init__(self, max_context_tokens: int = 6000):
        self.max_context_tokens = max_context_tokens

    def estimate_tokens(self, text: str) -> int:
        """Estimates token length for Traditional Chinese / English mixed text."""
        if not text:
            return 0
        # CJK characters typically consume ~1-2 tokens per char
        cjk_count = len(re.findall(r'[\u4e00-\u9fff]', text))
        non_cjk_words = len(re.findall(r'\b\w+\b', text))
        return int(cjk_count * 1.5 + non_cjk_words * 1.3)

    def truncate_transcript(self, transcript: str, max_tokens: int = 3000) -> str:
        """
        Sliding-window truncates older dialogue turns from transcript if token count exceeds max_tokens.
        Preserves header instructions and recent N dialogue turns.
        """
        if not transcript or self.estimate_tokens(transcript) <= max_tokens:
            return transcript

        lines = transcript.split("\n")
        header_lines = [l for l in lines if l.startswith("[系統]:") or "面試開始" in l]
        dialogue_lines = [l for l in lines if not (l.startswith("[系統]:") or "面試開始" in l)]

        # Keep dialogue turns from the end (most recent) backwards
        kept_dialogue = []
        accumulated_tokens = self.estimate_tokens("\n".join(header_lines))
        
        for line in reversed(dialogue_lines):
            line_tokens = self.estimate_tokens(line)
            if accumulated_tokens + line_tokens > max_tokens:
                break
            kept_dialogue.insert(0, line)
            accumulated_tokens += line_tokens

        truncated_summary = "[系統]: (更早期的問答對話已進行記憶摘要壓縮以控制 Token 長度...)\n"
        return "\n".join(header_lines) + "\n" + truncated_summary + "\n".join(kept_dialogue)

    def sanitize_prompt_kwargs(self, prompt_kwargs: Dict[str, Any], max_tokens: int = 5000) -> Dict[str, Any]:
        """
        Sanitizes and truncates prompt kwargs to prevent Context Window Overflow.
        """
        sanitized = dict(prompt_kwargs)
        
        # Truncate transcript if present
        if "transcript" in sanitized and isinstance(sanitized["transcript"], str):
            sanitized["transcript"] = self.truncate_transcript(sanitized["transcript"], max_tokens=max_tokens // 2)

        # Truncate candidate profile if excessively long
        if "candidate_profile" in sanitized and isinstance(sanitized["candidate_profile"], str):
            profile_text = sanitized["candidate_profile"]
            if self.estimate_tokens(profile_text) > (max_tokens // 2):
                sanitized["candidate_profile"] = profile_text[:3000] + "\n... (履歷其餘章節摘要截斷)"

        return sanitized

token_context_guard = TokenContextGuard()
