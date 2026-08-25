import os
import sys
import asyncio

# Ensure UTF-8 output encoding for Windows PowerShell
if sys.stdout and hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.services.document_parser import pdf_parser_service

TEST_PDF_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "test_files", "成大資工面試簡歷資料.pdf"))

async def run_day10_live_tests():
    print("==================================================", flush=True)
    print("UniMock AI - Day 10 Multimodal PDF Content Extractor Test", flush=True)
    print("==================================================", flush=True)
    print(f"Target PDF File: {TEST_PDF_PATH}", flush=True)

    if not os.path.exists(TEST_PDF_PATH):
        print(f"❌ Error: File not found at {TEST_PDF_PATH}", flush=True)
        return

    # Step 1: Multimodal Component Extraction (Text + Images)
    print("\n--- [Step 1] Multimodal Extraction (Text, Layout & Image Components) ---", flush=True)
    with open(TEST_PDF_PATH, "rb") as f:
        pdf_bytes = f.read()

    components = pdf_parser_service.extract_multimodal_components(pdf_bytes)
    print(f"Total Pages: {components['total_pages']}", flush=True)
    print(f"Total Embedded Image Components: {components['total_images']}", flush=True)
    print("Embedded Images Metadata List:")
    for img_meta in components["image_metadata"]:
        print(f"  - Page {img_meta['page']}: {img_meta['width']}x{img_meta['height']} px ({img_meta['format']}) - {img_meta['name']}")

    # Step 2: Live Multimodal AI Resume Analysis with Gemma-4-31B
    print("\n--- [Step 2] Live Multimodal Analysis with Gemma-4-31B ---", flush=True)
    result = await pdf_parser_service.parse_multimodal_resume(
        pdf_bytes=pdf_bytes,
        target_school="國立成功大學",
        target_major="資訊工程學系"
    )

    print("\nGemma Multimodal Analysis Output Result:\n", flush=True)
    print(result["multimodal_analysis_result"], flush=True)

    print("\n==================================================", flush=True)
    print("Day 10 Multimodal PDF Test Completed Successfully!", flush=True)
    print("==================================================", flush=True)

if __name__ == "__main__":
    asyncio.run(run_day10_live_tests())
