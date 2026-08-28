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
        # Detect invalid/meaningless/empty answer
        evasive_keywords = ["不知道", "不清楚", "沒想法", "隨便", "pass", "Pass", "PASS", "無", "沒有", "忘記", "123", "abc", "...", "？", "?"]
        is_evasive = any(kw in clean_text for kw in evasive_keywords) and length < 20
        is_invalid_answer = length < 5 or is_evasive

        is_too_brief = length < 30 and not is_invalid_answer

        # Check STAR dimension indicators
        has_action = any(kw in clean_text for kw in ["使用", "採用", "實作", "開發", "優化", "設計", "解決", "透過"])
        has_result = any(kw in clean_text for kw in ["成果", "提升", "縮短", "降低", "獎項", "第", "分", "O(", "效率", "成功"])

        star_score = (1 if length >= 30 else 0) + (1 if has_action else 0) + (1 if has_result else 0)
        requires_socratic_probe = is_invalid_answer or is_too_brief or star_score <= 1

        return {
            "length": length,
            "is_invalid_answer": is_invalid_answer,
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
        if quality_eval.get("is_invalid_answer"):
            return (
                "【考官極重要警告】：學生的回答極度簡短、無意義，或直接表示『不知道/沒有』，完全未對問題做出實質回應。\n"
                "【考官應對規範】：\n"
                "1. 嚴禁給予任何正面肯定、誇獎或『沒關係』這類緩和詞！\n"
                "2. 必須以嚴肅且客觀的面試官態度，直接點出該回答過於抽象或未回答到題目核心。\n"
                "3. 重申問題的核心切入點，並引導學生嘗試提出自己的推論或基礎理解。"
            )
        elif quality_eval["is_too_brief"]:
            return (
                "【考官觀察】：學生的回答過於簡短，缺乏具體技術細節。\n"
                "【蘇格拉底追問指引】：請追問學生：\n"
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
