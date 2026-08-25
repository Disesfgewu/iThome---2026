import io
import os
import pypdf
from typing import Dict, Any, List, Optional
from PIL import Image

from app.models.candidate_model import CandidateProfile
from app.services.gemma_llm import gemma_client

class PDFParserService:
    """
    Multimodal PDF Resume & Application Portfolio Document Parser Service.
    
    Capabilities:
    1. Text & Layout Extraction: Extracts structured text page-by-page using pypdf.
    2. Visual Image Component Extraction: Extracts embedded images (diagrams, architecture charts, certificates, tables).
    3. Multimodal Analysis via Gemma-4-31B: Analyzes document text + visual image metadata to synthesize CandidateProfile.
    """
    def extract_text_from_pdf_bytes(self, pdf_bytes: bytes) -> str:
        """Extracts all text content page-by-page from raw PDF bytes."""
        reader = pypdf.PdfReader(io.BytesIO(pdf_bytes))
        extracted_pages = []
        for idx, page in enumerate(reader.pages, 1):
            text = page.extract_text() or ""
            extracted_pages.append(f"--- [Page {idx}] ---\n{text.strip()}")
        return "\n\n".join(extracted_pages)

    def extract_text_from_pdf_file(self, filepath: str) -> str:
        """Extracts text from PDF file path."""
        with open(filepath, "rb") as f:
            return self.extract_text_from_pdf_bytes(f.read())

    def extract_multimodal_components(self, pdf_bytes: bytes) -> Dict[str, Any]:
        """
        Extracts both textual content and visual image metadata (diagrams, charts, photos) from PDF bytes.
        """
        reader = pypdf.PdfReader(io.BytesIO(pdf_bytes))
        total_pages = len(reader.pages)
        
        page_summaries = []
        total_images = 0
        image_metadata_list = []

        for idx, page in enumerate(reader.pages, 1):
            page_text = page.extract_text() or ""
            images_in_page = len(page.images)
            total_images += images_in_page

            page_img_details = []
            for img_idx, img_obj in enumerate(page.images, 1):
                try:
                    pil_img = Image.open(io.BytesIO(img_obj.data))
                    detail_str = f"Image #{img_idx} ({pil_img.format}, {pil_img.size[0]}x{pil_img.size[1]} px, Name: {img_obj.name})"
                    page_img_details.append(detail_str)
                    image_metadata_list.append({
                        "page": idx,
                        "name": img_obj.name,
                        "format": pil_img.format,
                        "width": pil_img.size[0],
                        "height": pil_img.size[1]
                    })
                except Exception as e:
                    page_img_details.append(f"Image #{img_idx} (Raw data: {len(img_obj.data)} bytes)")

            summary = (
                f"=== [頁次 Page {idx}/{total_pages}] ===\n"
                f"內嵌視覺圖片與圖表數量: {images_in_page} 個\n"
                f"圖片細節: {'; '.join(page_img_details) if page_img_details else '無影像圖片'}\n"
                f"頁面文字內文：\n{page_text.strip()}\n"
            )
            page_summaries.append(summary)

        return {
            "total_pages": total_pages,
            "total_images": total_images,
            "image_metadata": image_metadata_list,
            "full_document_text": "\n\n".join(page_summaries)
        }

    async def parse_multimodal_resume(
        self,
        pdf_bytes: bytes,
        target_school: str = "國立成功大學",
        target_major: str = "資訊工程學系"
    ) -> Dict[str, Any]:
        """
        Multimodal Analysis Engine:
        1. Extracts multimodal text & visual component metadata from PDF.
        2. Injects into `application_multimodal_analysis` System Prompt.
        3. Calls Gemma-4-31B LLM to extract structured CandidateProfile and key highlights.
        """
        components = self.extract_multimodal_components(pdf_bytes)
        doc_text = components["full_document_text"]

        # Call Gemma-4-31B for Multimodal Application Analysis
        analysis_result = await gemma_client.invoke_with_system_prompt(
            prompt_name="application_multimodal_analysis",
            user_input="",
            target_major=target_major,
            document_content=doc_text[:8000]  # Safe token context limit
        )

        return {
            "total_pages": components["total_pages"],
            "total_images": components["total_images"],
            "extracted_text_snippet": doc_text[:500] + "...",
            "multimodal_analysis_result": analysis_result
        }

pdf_parser_service = PDFParserService()
