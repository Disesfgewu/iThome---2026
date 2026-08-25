import uuid
from datetime import datetime
from typing import Dict, Any, List, Optional
from app.models.candidate_model import CandidateProfile

class SessionRepository:
    """
    In-Memory Session Repository managing Record DB and Q/A DB state.
    Stores interview session metadata, transcripts, candidate profiles, and evaluation reports.
    """
    def __init__(self):
        self._sessions: Dict[str, Dict[str, Any]] = {}

    def create_session(
        self,
        target_school: str,
        target_major: str,
        interview_mode: str,
        candidate_profile: Optional[CandidateProfile] = None
    ) -> str:
        session_id = f"sess_{uuid.uuid4().hex[:10]}"
        now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        profile = candidate_profile or CandidateProfile(
            target_school=target_school,
            target_major=target_major
        )

        self._sessions[session_id] = {
            "session_id": session_id,
            "target_school": target_school,
            "target_major": target_major,
            "interview_mode": interview_mode,
            "created_at": now_str,
            "candidate_profile": profile,
            "transcript_turns": [],
            "transcript_text": "[系統]: 面試開始。",
            "scoring_evaluation": "",
            "overall_strategic_report": ""
        }
        return session_id

    def get_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        return self._sessions.get(session_id)

    def add_question_turn(self, session_id: str, question_text: str):
        session = self.get_session(session_id)
        if not session:
            raise KeyError(f"Session '{session_id}' not found.")
        
        turn_idx = len(session["transcript_turns"]) + 1
        session["transcript_turns"].append({
            "turn": turn_idx,
            "question": question_text,
            "answer": ""
        })
        session["transcript_text"] += f"\n[考官]: {question_text}"

    def add_answer_turn(self, session_id: str, answer_text: str):
        session = self.get_session(session_id)
        if not session:
            raise KeyError(f"Session '{session_id}' not found.")

        if session["transcript_turns"]:
            session["transcript_turns"][-1]["answer"] = answer_text
        session["transcript_text"] += f"\n[學生]: {answer_text}"

    def update_reports(self, session_id: str, scoring_eval: str, overall_report: str):
        session = self.get_session(session_id)
        if not session:
            raise KeyError(f"Session '{session_id}' not found.")
        
        session["scoring_evaluation"] = scoring_eval
        session["overall_strategic_report"] = overall_report

    def list_all_sessions(self) -> List[Dict[str, Any]]:
        summaries = []
        for sess_id, sess in self._sessions.items():
            summaries.append({
                "session_id": sess_id,
                "target_school": sess["target_school"],
                "target_major": sess["target_major"],
                "interview_mode": sess["interview_mode"],
                "created_at": sess["created_at"],
                "total_turns": len(sess["transcript_turns"]),
                "has_report": bool(sess["overall_strategic_report"])
            })
        return summaries

session_repository = SessionRepository()
