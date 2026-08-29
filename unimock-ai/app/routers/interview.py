import json
from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
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
from app.services.memory_manager import memory_manager

router = APIRouter(prefix="/api/interview", tags=["Interview Session & Chat"])

@router.post("/setup", response_model=InterviewSetupResponse)
async def setup_interview_session(req: InterviewSetupRequest):
    """
    Initializes interview session, computes 3072-dim RAG vector embeddings, generates initial question via Gemma-4-31B,
    and initializes LangChain ConversationTokenBufferMemory.
    """
    session_id = session_repository.create_session(
        target_school=req.target_school,
        target_major=req.target_major,
        interview_mode=req.interview_mode,
        candidate_profile=req.candidate_profile
    )

    # Generate initial ice-breaking self-introduction question tailored to target school & major
    first_question = (
        f"歡迎來到{req.target_school} {req.target_major}的面試模擬現場。請您先進行約 1 到 2 分鐘的自我介紹，"
        f"說明您的報考動機，以及您最具代表性的個人優勢與專長？"
    )
    
    # Pre-retrieve RAG seed questions for subsequent turns
    rag_res = await rag_service.generate_rag_question_for_candidate(
        candidate_profile=req.candidate_profile or req.target_major,
        target_school=req.target_school,
        target_major=req.target_major,
        interview_mode=req.interview_mode
    )

    session_repository.add_question_turn(session_id, first_question)
    
    # Initialize LangChain Memory and record first AI question
    memory_manager.get_or_create_messages(session_id)
    memory_manager.add_ai_message(session_id, first_question)

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
    evaluates answer quality via FollowupAgent for Socratic probing, updates LangChain Memory,
    truncates context with TokenContextGuard, and generates follow-up question via Gemma-4-31B.
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

    # 2. Update transcript history & LangChain Memory with user answer
    session_repository.add_answer_turn(req.session_id, req.user_answer)
    memory_manager.add_user_message(req.session_id, req.user_answer)

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

    # 5. Truncate context with sliding-window TokenContextGuard / Memory Buffer String
    safe_transcript = token_context_guard.truncate_transcript(
        session["transcript_text"],
        max_tokens=3000
    )

    # 6. Generate follow-up response / question via Gemma-4-31B with stage & socratic instructions
    user_prompt_with_instructions = (
        f"【面試階段重點】：{stage_instruction}\n"
        f"【蘇格拉底追問指引】：{socratic_instruction}\n"
        f"【學生最新回答】：{req.user_answer}\n\n"
        f"【最高發問規範】：\n"
        f"1. 必須嚴格針對學生剛才回答中提及的『具體技術關鍵字、專案成果或學習經驗』進行精準銜接追問（絕不文不對題）。\n"
        f"2. 嚴禁重複先前已問過或學生已說明的問題。\n"
        f"3. 僅直接輸出唯一一句繁體中文發問，不要任何 Alternative:、Option: 或草稿前綴！"
    )

    next_question = await gemma_client.invoke_with_system_prompt(
        prompt_name="response_generation",
        user_input=user_prompt_with_instructions,
        target_major=session["target_major"],
        candidate_profile=session["candidate_profile"].to_structured_text(),
        transcript=safe_transcript
    )

    session_repository.add_question_turn(req.session_id, next_question)
    memory_manager.add_ai_message(req.session_id, next_question)

    return AnswerSubmitResponse(
        session_id=req.session_id,
        user_answer=req.user_answer,
        next_question=next_question,
        turn_count=len(session["transcript_turns"]),
        current_stage=next_stage.value,
        is_finished=is_finished
    )

@router.post("/answer-stream")
async def submit_user_answer_stream(req: AnswerSubmitRequest):
    """
    Submits user answer and returns real-time SSE (Server-Sent Events) token stream from Gemma-4-31B.
    """
    session = session_repository.get_session(req.session_id)
    if not session:
        raise HTTPException(status_code=404, detail=f"Session '{req.session_id}' not found.")

    if session.get("is_finished"):
        async def finished_generator():
            done_payload = json.dumps({
                "done": True,
                "full_text": "[系統]: 本場面試問答已圓滿結束。您可以點擊產出戰略評分報告。",
                "turn_count": len(session["transcript_turns"]),
                "current_stage": session["current_stage"],
                "is_finished": True
            }, ensure_ascii=False)
            yield f"data: {done_payload}\n\n"
        return StreamingResponse(finished_generator(), media_type="text/event-stream")

    # 1. Security Guardrail Verification
    is_safe, reason = security_guardrail.verify_input_safety(req.user_answer)
    if not is_safe:
        raise HTTPException(status_code=400, detail=f"Input blocked by Security Guardrail: {reason}")

    # 2. Update transcript history & LangChain Memory with user answer
    session_repository.add_answer_turn(req.session_id, req.user_answer)
    memory_manager.add_user_message(req.session_id, req.user_answer)

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

    # 6. Build prompt with instructions
    user_prompt_with_instructions = (
        f"【面試階段重點】：{stage_instruction}\n"
        f"【蘇格拉底追問指引】：{socratic_instruction}\n"
        f"【學生最新回答】：{req.user_answer}\n\n"
        f"【最高發問規範】：\n"
        f"1. 必須嚴格針對學生剛才回答中提及的『具體技術關鍵字、專案成果或學習經驗』進行精準銜接追問（絕不文不對題）。\n"
        f"2. 嚴禁重複先前已問過或學生已說明的問題。\n"
        f"3. 僅直接輸出唯一一句繁體中文發問，不要任何 Alternative:、Option: 或草稿前綴！"
    )

    async def sse_stream_generator():
        accumulated_text = ""
        try:
            async for token in gemma_client.astream_with_system_prompt(
                prompt_name="response_generation",
                user_input=user_prompt_with_instructions,
                target_major=session["target_major"],
                candidate_profile=session["candidate_profile"].to_structured_text(),
                transcript=safe_transcript
            ):
                accumulated_text += token
                chunk_payload = json.dumps({"text": token, "done": False}, ensure_ascii=False)
                yield f"data: {chunk_payload}\n\n"
        except Exception as e:
            error_payload = json.dumps({"text": f" [流式生成中斷: {str(e)}]", "done": False}, ensure_ascii=False)
            yield f"data: {error_payload}\n\n"

        # Finalize turn
        clean_question = gemma_client._strip_thinking_blocks(accumulated_text)
        session_repository.add_question_turn(req.session_id, clean_question)
        memory_manager.add_ai_message(req.session_id, clean_question)

        meta_payload = json.dumps({
            "done": True,
            "full_text": clean_question,
            "turn_count": len(session["transcript_turns"]),
            "current_stage": next_stage.value,
            "is_finished": is_finished
        }, ensure_ascii=False)
        yield f"data: {meta_payload}\n\n"

    return StreamingResponse(
        sse_stream_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"
        }
    )
