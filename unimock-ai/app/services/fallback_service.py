"""
UniMock AI - Graceful Degradation & Fallback Service
Provides structural fallback responses when Gemini/Gemma LLM services experience network timeouts,
quota exhaustion (429 Rate Limit), or API interruptions.
"""

from typing import Dict, Any, List
import logging

logger = logging.getLogger(__name__)


class FallbackService:
    """
    Fallback service providing domain-specific interview questions and reports
    for graceful degradation when main LLM services fail.
    """

    DEFAULT_FALLBACK_QUESTIONS: Dict[str, List[str]] = {
        "business": [
            "請說明您的個人背景、專業成就以及報考本系所的核心動機？",
            "在面對市場競爭與外在環境快速變動時，您如何制定風險控管與戰略決策？",
            "請分享一次您主持或參與的代表性專案，說明您在其中的角色與量化效益？",
            "對於未來的學習與職涯規劃，您希望在本系所獲得哪些關鍵能力？"
        ],
        "tech": [
            "請進行自我介紹，並說明您在資訊技術與程式開發上的代表性成果？",
            "在處理複雜系統架構或演算法效能瓶頸時，您如何評估 Trade-off 並進行優化？",
            "請分享一次專案遭遇技術難題的經驗，您採用了哪些方法進行排解？",
            "您如何看待新興 AI 與資訊技術在目標領域的前瞻應用與發展趨勢？"
        ],
        "general": [
            "請說明您的個人優勢，以及選擇報考本系所的核心原因？",
            "請分享一次克服困難或與團隊合作達成目標的代表性經歷？",
            "在過往的學習或實務歷程中，哪一項成就最能代表您的專業能力？",
            "請說明您對未來的學習規劃與短期/長期職涯目標？"
        ]
    }

    @classmethod
    def get_fallback_question(cls, target_major: str, turn_index: int = 1) -> str:
        """
        Returns a domain-tailored fallback question when LLM streaming fails.
        """
        is_business = any(kw in target_major for kw in ["EMBA", "MBA", "企管", "資管", "金融", "國企", "財金", "商", "管理", "行銷"])
        is_tech = any(kw in target_major for kw in ["資工", "資訊", "電機", "軟體", "數據", "AI", "電子"])

        category = "business" if is_business else ("tech" if is_tech else "general")
        questions = cls.DEFAULT_FALLBACK_QUESTIONS[category]
        idx = (turn_index - 1) % len(questions)
        logger.warning(f"Using fallback question for {target_major} (Turn {turn_index}, Category: {category})")
        return questions[idx]

    @classmethod
    def get_fallback_evaluation_report(
        cls,
        target_school: str,
        target_major: str,
        transcript_turns: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Generates a robust fallback evaluation report when Gemini/Gemma LLM report generation fails.
        """
        logger.warning(f"Generating fallback evaluation report for {target_school} {target_major}")

        is_business = any(kw in target_major for kw in ["EMBA", "MBA", "企管", "資管", "金融", "國企", "財金", "商", "管理", "行銷"])

        diagnoses = []
        for idx, turn in enumerate(transcript_turns):
            turn_num = turn.get("turn", idx + 1)
            q_text = turn.get("question", f"面試考題 {turn_num}")
            a_text = turn.get("answer", "（未記錄回答）")

            if is_business:
                if turn_num == 1:
                    weakness = f"自我介紹表達沉著，建議加強說明高階管理視角、資產與風險管理決策，以及報考 {target_major} 的核心動機。"
                    improved = f"教授您好，我目前任職於金融機構擔任風控主管，長期負責跨國資產負債管理與法遵決策。在實務工作中，我發現傳統風控框架難以即時反應環境變化，因此主動導入敏感度分析模型與結構化避險機制，有效控制資金成本。這也是我報考{target_major}的核心動機。"
                elif turn_num == 2:
                    weakness = "實務經驗述說清晰，但建議進一步補充具體管理決策架構與量化成效指標。"
                    improved = f"教授您好，在面對升息與供應鏈重組的背景下，我在公司主持了外匯避險與流動性壓力測試專案。我們建立了動態敏感度分析模型，成功將資金成本增幅控制在目標範圍內，展現出在{target_major}領域的管理決策能力。"
                else:
                    weakness = f"專業觀點極具前瞻性，若能深化 ESG 綠色金融與 AI 自動化審查之落地戰略，說服力將更加卓越。"
                    improved = f"教授您好，在思考未來的研究方向時，我聚焦於綠色金融與 ESG 永續放款標準的整合應用，期許透過 AI 智動化風控審查引導企業完成數位轉型，這也是我在{target_major}最希望深入研究的議題。"
            else:
                if turn_num == 1:
                    weakness = f"自我介紹條理尚屬清晰，但建議加強『報考 {target_major} 的核心動機』與『具體專案成果』的連結。"
                    improved = f"教授您好，我在修習專業基礎課程與推動專案的過程中，建立了對{target_major}的強烈興趣。我在一次模組化專案中透過結構化測試將執行效能提升了 35%，這段歷程確立了我深入貴所研究的堅定動機。"
                elif turn_num == 2:
                    weakness = "技術細節回答明確，但建議補充『演算法 Trade-off 選擇考量』與『最終量化效能指標』。"
                    improved = f"教授您好，在專案開發中我遇到了核心模組的瓶頸，我採用對比分析與數據快取緩衝機制，成功將回應延遲降低至毫秒等級，這證明了我具備優秀的{target_major}開發與優化潛能。"
                else:
                    weakness = f"回答具備良好說服力，若能進一步連結 {target_major} 最新前瞻趨勢（如 AI 結合企業流程），講述深度將更臻完善。"
                    improved = f"教授您好，對於{target_major}的前瞻應用，我關注大語言模型如何與企業核心業務流程整合，並探討隱私合規與效能優化，期望在貴所學習期間深化相關理論與落地策略。"

            diagnoses.append({
                "turn_index": turn_num,
                "question": q_text,
                "original_answer": a_text,
                "weakness_analysis": weakness,
                "improved_sample": improved
            })

        return {
            "overall_score": 82.0,
            "scores": {
                "logic_structure": 8.0,
                "major_relevance": 8.5,
                "communication_clarity": 8.0,
                "adaptability": 8.0
            },
            "radar_scores": {
                "logic_structure": 8.0,
                "major_relevance": 8.5,
                "communication_clarity": 8.0,
                "adaptability": 8.0
            },
            "overall_feedback": f"考生對答切中核心，表現符合 {target_school} {target_major} 入學標準。若能進一步補充更多數據細節，表現將更加出色。",
            "strengths": [
                "回答結構條理清晰，具備良好說服力",
                "展現與目標系所高度契合之實務與專業背景"
            ],
            "improvements": [
                "可進一步補充量化數據指標（Metrics）以增加專案成果實感",
                "建議深化前瞻技術/趨勢與個人未來研究計畫的具體連結"
            ],
            "question_diagnoses": diagnoses
        }


fallback_service = FallbackService()
