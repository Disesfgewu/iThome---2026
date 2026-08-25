from fastapi import APIRouter, HTTPException
from app.models.api_schemas import (
    InterviewSetupRequest,
    InterviewSetupResponse,
    AnswerSubmitRequest,
    AnswerSubmitResponse
)
from app.repositories.session_repository import session_repository
from app.services.rag_service import rag_service
from app.services.gemma_llm import gemma_client
from app.services.security_guardrail import security_guardrail
from app.services.context_manager import token_context_guard
from app.services.state_machine import InterviewStage, interview_state_machine
from app.services.followup_agent import followup_agent

router = APIRouter(prefix="/api/interview", tags=["Interview Session & Chat"])

@router.post("/setup", response_model=InterviewSetupResponse)
async def setup_interview_session(req: InterviewSetupRequest):
    """
    Initializes interview session, computes 3072-dim RAG vector embeddings, and generates initial question via Gemma-4-31B.
    """
    session_id = session_repository.create_session(
        target_school=req.target_school,
        target_major=req.target_major,
        interview_mode=req.interview_mode,
        candidate_profile=req.candidate_profile
    )

    # Generate initial RAG question
    rag_res = await rag_service.generate_rag_question_for_candidate(
        candidate_profile=req.candidate_profile or req.target_major,
        target_school=req.target_school,
        target_major=req.target_major,
        interview_mode=req.interview_mode
    )

    first_question = rag_res["generated_question"]
    session_repository.add_question_turn(session_id, first_question)
    session = session_repository.get_session(session_id)

    return InterviewSetupResponse(
        session_id=session_id,
        target_school=req.target_school,
        target_major=req.target_major,
        interview_mode=req.interview_mode,
        current_stage=session["current_stage"],
        first_question=first_question,
        rag_seed_questions_count=len(rag_res["rag_seed_questions"])
    )

@router.post("/answer", response_model=AnswerSubmitResponse)
async def submit_user_answer(req: AnswerSubmitRequest):
    """
    Submits user answer, runs SecurityGuardrail check, applies InterviewStateMachine stage instruction,
    evaluates answer quality via FollowupAgent for Socratic probing, truncates context with TokenContextGuard,
    and generates follow-up question via Gemma-4-31B.
    """
    session = session_repository.get_session(req.session_id)
    if not session:
        raise HTTPException(status_code=404, detail=f"Session '{req.session_id}' not found.")

    if session.get("is_finished"):
        return AnswerSubmitResponse(
            session_id=req.session_id,
            user_answer=req.user_answer,
            next_question="[系統]: 本場面試問答已圓滿結束。您可以點擊產出戰略評分報告。",
            turn_count=len(session["transcript_turns"]),
            current_stage=session["current_stage"],
            is_finished=True
        )

    # 1. Security Guardrail Verification
    is_safe, reason = security_guardrail.verify_input_safety(req.user_answer)
    if not is_safe:
        raise HTTPException(status_code=400, detail=f"Input blocked by Security Guardrail: {reason}")

    # 2. Update transcript history with user answer
    session_repository.add_answer_turn(req.session_id, req.user_answer)

    # 3. Evaluate answer quality via FollowupAgent
    quality_eval = followup_agent.evaluate_answer_quality(req.user_answer)
    socratic_instruction = followup_agent.build_socratic_prompt(
        question=session["transcript_turns"][-1]["question"],
        answer=req.user_answer,
        quality_eval=quality_eval
    )

    # 4. Determine next turn stage instruction from InterviewStateMachine
    turn_count = len(session["transcript_turns"]) + 1
    next_stage, is_finished = interview_state_machine.get_stage_for_turn(turn_count)
    stage_instruction = interview_state_machine.get_stage_instruction(next_stage)

    # 5. Truncate context with sliding-window TokenContextGuard
    safe_transcript = token_context_guard.truncate_transcript(
        session["transcript_text"],
        max_tokens=3000
    )

    # 6. Generate follow-up response / question via Gemma-4-31B with stage & socratic instructions
    user_prompt_with_instructions = (
        f"{stage_instruction}\n"
        f"{socratic_instruction}\n"
        f"【學生最新回答】：{req.user_answer}"
    )

    next_question = await gemma_client.invoke_with_system_prompt(
        prompt_name="response_generation",
        user_input=user_prompt_with_instructions,
        target_major=session["target_major"],
        candidate_profile=session["candidate_profile"].to_structured_text(),
        transcript=safe_transcript
    )

    session_repository.add_question_turn(req.session_id, next_question)

    return AnswerSubmitResponse(
        session_id=req.session_id,
        user_answer=req.user_answer,
        next_question=next_question,
        turn_count=len(session["transcript_turns"]),
        current_stage=next_stage.value,
        is_finished=is_finished
    )
