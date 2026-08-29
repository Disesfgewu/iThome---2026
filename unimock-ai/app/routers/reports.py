from fastapi import APIRouter, HTTPException
from app.models.api_schemas import ReportGenerateRequest, ReportGenerateResponse
from app.repositories.session_repository import session_repository
from app.services.evaluation_service import evaluation_service

router = APIRouter(prefix="/api/reports", tags=["Evaluation & Strategic Reports"])

@router.post("/generate", response_model=ReportGenerateResponse)
async def generate_evaluation_report(req: ReportGenerateRequest):
    """
    Aggregates entire Q/A DB transcript history, executes Gemma-4-31B rubric scoring via EvaluationService,
    computes multi-dimensional radar scores, and saves to Record DB.
    """
    session = session_repository.get_session(req.session_id)
    if not session:
        raise HTTPException(status_code=404, detail=f"Session '{req.session_id}' not found.")

    transcript = session["transcript_text"]
    profile_text = session["candidate_profile"].to_structured_text()

    # Execute EvaluationService to compute scoring and strategic report
    eval_res = await evaluation_service.evaluate_interview_session(
        session_id=req.session_id,
        target_school=session["target_school"],
        target_major=session["target_major"],
        candidate_profile_text=profile_text,
        transcript_text=transcript,
        transcript_turns=session.get("transcript_turns", [])
    )

    # Save to Session Repository
    session_repository.update_reports(
        req.session_id,
        scoring_eval=eval_res["scoring_evaluation_text"],
        overall_report=eval_res["overall_strategic_report"]
    )

    return ReportGenerateResponse(
        session_id=req.session_id,
        target_school=session["target_school"],
        target_major=session["target_major"],
        total_turns=len(session["transcript_turns"]),
        overall_score=eval_res["overall_score"],
        radar_scores=eval_res["radar_scores"],
        strengths=eval_res.get("strengths", []),
        improvements=eval_res.get("improvements", []),
        question_diagnoses=eval_res.get("question_diagnoses", []),
        scoring_evaluation=eval_res["scoring_evaluation_text"],
        overall_strategic_report=eval_res["overall_strategic_report"]
    )
