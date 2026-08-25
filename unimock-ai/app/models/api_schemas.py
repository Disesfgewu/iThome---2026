from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
from app.models.candidate_model import CandidateProfile

class PDFUploadResponse(BaseModel):
    """Response DTO for PDF Resume Upload."""
    status: str = "success"
    filename: str
    total_pages: int
    total_images: int
    candidate_profile: CandidateProfile

class InterviewSetupRequest(BaseModel):
    """Request DTO for Interview Session Setup."""
    target_school: str = Field(..., json_schema_extra={"example": "國立台灣大學"})
    target_major: str = Field(..., json_schema_extra={"example": "資訊工程學系"})
    interview_mode: str = Field(default="標準二階面試", json_schema_extra={"example": "頂大嚴謹模式"})
    candidate_profile: Optional[CandidateProfile] = None

class InterviewSetupResponse(BaseModel):
    """Response DTO for Interview Session Setup."""
    session_id: str
    target_school: str
    target_major: str
    interview_mode: str
    first_question: str
    rag_seed_questions_count: int

class AnswerSubmitRequest(BaseModel):
    """Request DTO for Submitting User Answer."""
    session_id: str
    user_answer: str

class AnswerSubmitResponse(BaseModel):
    """Response DTO for User Answer Submission."""
    session_id: str
    user_answer: str
    next_question: str
    turn_count: int

class ReportGenerateRequest(BaseModel):
    """Request DTO for Report Generation."""
    session_id: str

class ReportGenerateResponse(BaseModel):
    """Response DTO for Report Generation."""
    session_id: str
    target_school: str
    target_major: str
    total_turns: int
    scoring_evaluation: str
    overall_strategic_report: str

class RecordSummaryResponse(BaseModel):
    """Response DTO for Session Record Summary."""
    session_id: str
    target_school: str
    target_major: str
    interview_mode: str
    created_at: str
    total_turns: int
    has_report: bool
