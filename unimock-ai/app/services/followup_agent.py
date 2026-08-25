import re
from typing import Dict, Any, Tuple
from app.services.gemma_llm import gemma_client

class FollowupAgent:
    """
    Socratic Follow-up Agent optimizing interview dialogue quality.
    Evaluates candidate answer brevity, STAR completeness, and generates targeted Socratic probing questions.
    """
    def evaluate_answer_quality(self, answer: str) -> Dict[str, Any]:
        """
        Evaluates answer quality based on character length and structural completeness keywords.
        Returns quality evaluation metrics.
        """
        clean_text = answer.strip()
        length = len(clean_text)
        is_too_brief = length < 30

        # Check STAR dimension indicators
        has_action = any(kw in clean_text for kw in ["使用", "採用", "實作", "開發", "優化", "設計", "解決", "透過"])
        has_result = any(kw in clean_text for kw in ["成果", "提升", "縮短", "降低", "獎項", "第", "分", "O(", "效率", "成功"])

        star_score = (1 if length >= 30 else 0) + (1 if has_action else 0) + (1 if has_result else 0)
        requires_socratic_probe = is_too_brief or star_score <= 1

        return {
            "length": length,
            "is_too_brief": is_too_brief,
            "has_action": has_action,
            "has_result": has_result,
            "star_score": star_score,
            "requires_socratic_probe": requires_socratic_probe
        }

    def build_socratic_prompt(self, question: str, answer: str, quality_eval: Dict[str, Any]) -> str:
        """
        Builds Socratic prompt instruction based on quality metrics.
        """
        if quality_eval["is_too_brief"]:
            return (
                "【考官觀察】：學生的回答過於簡短，缺乏具體技術細節。\n"
                "【蘇格拉底追問指引】：請以鼓勵但不放過細節的方式，追問學生：\n"
                "1. 為什麼 (Why) 做這個選擇？\n"
                "2. 具體 (How) 是如何實作與克服技術困難的？"
            )
        elif quality_eval["star_score"] <= 1:
            return (
                "【考官觀察】：學生的回答缺乏 STAR 原則中的具體行動 (Action) 或量化結果 (Result)。\n"
                "【蘇格拉底追問指引】：請點出學生回答中抽象模糊之處，追問其具體的演算法權衡 (Trade-off) 與實質成果 (What)。"
            )
        else:
            return "【考官觀察】：學生回答結構完整，請深化技術點並順暢推動面試進度。"

followup_agent = FollowupAgent()
