import os
import sys
import pytest
import io
import asyncio
import pypdf

# Reconfigure stdout for Windows console UTF-8 support
if sys.stdout and hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

from app.services.document_parser import pdf_parser_service, PDFParserService

TEST_PDF_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "test_files", "成大資工面試簡歷資料.pdf"))

def _create_sample_pdf_bytes() -> bytes:
    """Helper to generate a lightweight dummy PDF in-memory for PII-safe automated testing."""
    writer = pypdf.PdfWriter()
    page = writer.add_blank_page(width=595, height=842)
    # Add dummy text stream
    buf = io.BytesIO()
    writer.write(buf)
    return buf.getvalue()

def test_pdf_multimodal_extraction_with_fallback():
    """Verify PDFParserService extracts text, pages, and components from PDF bytes."""
    if os.path.exists(TEST_PDF_PATH):
        with open(TEST_PDF_PATH, "rb") as f:
            pdf_bytes = f.read()
    else:
        pdf_bytes = _create_sample_pdf_bytes()

    components = pdf_parser_service.extract_multimodal_components(pdf_bytes)
    assert isinstance(components, dict)
    assert "total_pages" in components
    assert "full_document_text" in components
    assert components["total_pages"] > 0

def test_multimodal_gemma_resume_analysis_with_fallback():
    """Verify end-to-end multimodal PDF parsing with Gemma-4-31B."""
    async def _test():
        if os.path.exists(TEST_PDF_PATH):
            with open(TEST_PDF_PATH, "rb") as f:
                pdf_bytes = f.read()
        else:
            pdf_bytes = _create_sample_pdf_bytes()

        result = await pdf_parser_service.parse_multimodal_resume(
            pdf_bytes=pdf_bytes,
            target_school="國立成功大學",
            target_major="資訊工程學系"
        )
        assert "total_pages" in result
        assert "multimodal_analysis_result" in result
        assert len(result["multimodal_analysis_result"].strip()) > 0
        safe_preview = result["multimodal_analysis_result"][:120].encode("ascii", "ignore").decode("ascii") or "Multimodal analysis OK"
        print(f"\n[Multimodal Resume Analysis Output Preview]: {safe_preview}")

    asyncio.run(_test())

if __name__ == "__main__":
    pytest.main(["-v", __file__])
