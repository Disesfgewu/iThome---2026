from fastapi import APIRouter, HTTPException
from app.models.api_schemas import ReportGenerateRequest, ReportGenerateResponse
from app.repositories.session_repository import session_repository
from app.services.gemma_llm import gemma_client

router = APIRouter(prefix="/api/reports", tags=["Evaluation & Strategic Reports"])

@router.post("/generate", response_model=ReportGenerateResponse)
async def generate_evaluation_report(req: ReportGenerateRequest):
    """
    Aggregates entire Q/A DB transcript history, executes Gemma-4-31B rubric scoring and strategic analysis, and saves to Record DB.
    """
    session = session_repository.get_session(req.session_id)
    if not session:
        raise HTTPException(status_code=404, detail=f"Session '{req.session_id}' not found.")

    transcript = session["transcript_text"]
    profile_text = session["candidate_profile"].to_structured_text()

    # 1. Generate 4-dimension Rubric Scoring Evaluation
    scoring_eval = await gemma_client.invoke_with_system_prompt(
        prompt_name="scoring_evaluation",
        user_input="",
        target_major=session["target_major"],
        transcript=transcript
    )

    # 2. Generate Overall Strategic Report
    overall_report = await gemma_client.invoke_with_system_prompt(
        prompt_name="overall_analysis",
        user_input="",
        target_school=session["target_school"],
        target_major=session["target_major"],
        candidate_profile=profile_text,
        transcript=transcript,
        aggregated_scores=scoring_eval
    )

    # 3. Update Record DB
    session_repository.update_reports(req.session_id, scoring_eval, overall_report)

    return ReportGenerateResponse(
        session_id=req.session_id,
        target_school=session["target_school"],
        target_major=session["target_major"],
        total_turns=len(session["transcript_turns"]),
        scoring_evaluation=scoring_eval,
        overall_strategic_report=overall_report
    )
