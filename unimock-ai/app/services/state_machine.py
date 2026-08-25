from enum import Enum
from typing import Dict, Any, Tuple

class InterviewStage(str, Enum):
    INTRO = "INTRO"                                # 階段一：破冰與自我介紹與申請動機
    PORTFOLIO_DEEP_DIVE = "PORTFOLIO_DEEP_DIVE"    # 階段二：備審自傳與專案經歷深挖
    SITUATIONAL_CHALLENGE = "SITUATIONAL_CHALLENGE"# 階段三：專業概念與臨場情境考驗
    WRAP_UP = "WRAP_UP"                            # 階段四：面試結束與收尾

STAGE_INSTRUCTIONS: Dict[InterviewStage, str] = {
    InterviewStage.INTRO: (
        "【當前面試階段：1. 自我介紹與申請動機 (INTRO)】\n"
        "請熱情親切地歡迎學生，針對目標校系的申請動機與個人的核心特點進行破冰發問。"
    ),
    InterviewStage.PORTFOLIO_DEEP_DIVE: (
        "【當前面試階段：2. 備審自傳與專案經歷深挖 (PORTFOLIO_DEEP_DIVE)】\n"
        "請針對學生備審歷程中的專案競賽、成績亮點或具體經歷進行深入追問與細節質疑。"
    ),
    InterviewStage.SITUATIONAL_CHALLENGE: (
        "【當前面試階段：3. 專業概念與臨場情境考驗 (SITUATIONAL_CHALLENGE)】\n"
        "請提出切中目標學系專業的技術瓶頸考驗、演算法權衡 (Trade-off) 或臨場情境決策題。"
    ),
    InterviewStage.WRAP_UP: (
        "【當前面試階段：4. 面試結束與收尾 (WRAP_UP)】\n"
        "本場面試問答已圓滿結束。請給予學生肯定與簡短總結評語，告知學生面試已結束，準備進行全面評分。"
    )
}

class InterviewStateMachine:
    """
    Finite State Machine controlling 4-phase interview dialogue progression.
    Determines current stage, transitions based on turn count, and injects stage instructions.
    """
    def __init__(self, max_turns: int = 6):
        self.max_turns = max_turns

    def get_stage_for_turn(self, turn_count: int) -> Tuple[InterviewStage, bool]:
        """
        Determines current InterviewStage and is_finished status based on turn_count.
        - Turn 1: INTRO
        - Turn 2~4: PORTFOLIO_DEEP_DIVE
        - Turn 5~5: SITUATIONAL_CHALLENGE
        - Turn 6+: WRAP_UP (Finished)
        """
        if turn_count <= 1:
            return InterviewStage.INTRO, False
        elif 2 <= turn_count <= 4:
            return InterviewStage.PORTFOLIO_DEEP_DIVE, False
        elif turn_count == 5:
            return InterviewStage.SITUATIONAL_CHALLENGE, False
        else:
            return InterviewStage.WRAP_UP, True

    def get_stage_instruction(self, stage: InterviewStage) -> str:
        return STAGE_INSTRUCTIONS.get(stage, "")

interview_state_machine = InterviewStateMachine()
