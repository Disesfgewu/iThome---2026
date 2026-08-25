from fastapi import APIRouter, UploadFile, File, HTTPException, Form
from app.models.api_schemas import PDFUploadResponse
from app.models.candidate_model import CandidateProfile
from app.services.document_parser import pdf_parser_service

router = APIRouter(prefix="/api/resume", tags=["Resume & PDF Parser"])

@router.post("/upload-pdf", response_model=PDFUploadResponse)
async def upload_pdf_resume(
    file: UploadFile = File(...),
    target_school: str = Form(default="國立成功大學"),
    target_major: str = Form(default="資訊工程學系")
):
    """
    Upload PDF Resume / Portfolio, extract multimodal text and image metadata, and run Gemma-4-31B analysis.
    """
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are supported.")

    pdf_bytes = await file.read()
    if not pdf_bytes:
        raise HTTPException(status_code=400, detail="Empty PDF file uploaded.")

    # 1. Extract multimodal components & run Gemma 4 multimodal analysis
    parse_res = await pdf_parser_service.parse_multimodal_resume(
        pdf_bytes=pdf_bytes,
        target_school=target_school,
        target_major=target_major
    )

    # 2. Build structured CandidateProfile
    candidate_profile = CandidateProfile(
        target_school=target_school,
        target_major=target_major,
        autobiography=parse_res["multimodal_analysis_result"][:300]
    )

    return PDFUploadResponse(
        status="success",
        filename=file.filename,
        total_pages=parse_res["total_pages"],
        total_images=parse_res["total_images"],
        candidate_profile=candidate_profile
    )
