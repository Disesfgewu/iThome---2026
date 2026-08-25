from typing import List, Dict, Any
from fastapi import APIRouter, HTTPException
from app.models.api_schemas import RecordSummaryResponse
from app.repositories.session_repository import session_repository

router = APIRouter(prefix="/api/records", tags=["Interview Session Records"])

@router.get("/list", response_model=List[RecordSummaryResponse])
async def list_interview_records():
    """
    Returns summaries of all past interview sessions stored in Record DB.
    """
    return session_repository.list_all_sessions()

@router.get("/{session_id}")
async def get_interview_record_detail(session_id: str) -> Dict[str, Any]:
    """
    Retrieves complete interview session details, including transcript Q/A turns and evaluation reports.
    """
    session = session_repository.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail=f"Record for session '{session_id}' not found.")
    
    return {
        "session_id": session["session_id"],
        "target_school": session["target_school"],
        "target_major": session["target_major"],
        "interview_mode": session["interview_mode"],
        "created_at": session["created_at"],
        "transcript_turns": session["transcript_turns"],
        "scoring_evaluation": session["scoring_evaluation"],
        "overall_strategic_report": session["overall_strategic_report"]
    }
