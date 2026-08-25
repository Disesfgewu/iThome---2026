import argparse
import json
import os
import re
import sys
import time

# Ensure UTF-8 output encoding for Windows PowerShell / CMD
if sys.stdout and hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

# Ensure root unimock-ai directory is in PYTHONPATH
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.services.embedding_service import embedding_service

def embed_with_retry(text: str, max_retries: int = 10):
    """
    Embeds text with automatic handling for Google AI Studio 100 RPM Rate Limit.
    If 429 Quota Exceeded occurs, parses retry_delay (e.g. 32s) or sleeps 35s before retrying.
    """
    for attempt in range(1, max_retries + 1):
        try:
            return embedding_service.embed_query(text)
        except Exception as e:
            err_msg = str(e)
            if "429" in err_msg or "Quota" in err_msg or "Resource" in err_msg:
                # Try to extract retry_delay from Google API error message
                match = re.search(r"retry in ([0-9\.]+)s", err_msg, re.IGNORECASE)
                if match:
                    wait_sec = float(match.group(1)) + 2.0
                else:
                    wait_sec = 35.0

                print(f"\n[429 RPM Limit] Hit 100 RPM Free Tier limit. Pausing {wait_sec:.1f}s for quota reset (Retry attempt {attempt}/{max_retries})...")
                time.sleep(wait_sec)
            elif attempt < max_retries:
                print(f"\n[Network Retry] {err_msg[:60]}. Retrying in 5s (Attempt {attempt}/{max_retries})...")
                time.sleep(5.0)
            else:
                raise e

def incremental_preembed(db_filepath: str, start_idx: int = 0, end_idx: int = None, force_reembed: bool = False, batch_save_interval: int = 50, pacing_delay: float = 0.65):
    """
    Strict Pre-embedding Engine for UniMock AI with 100 RPM Pacing & Retry.
    - Pacing delay of 0.65s guarantees ~90 requests/minute to stay under 100 RPM limit.
    - Auto-pauses 35s if 429 Quota Exceeded occurs and resumes without crashing.
    """
    if not os.path.exists(db_filepath):
        print(f"Error: Database file {db_filepath} not found!")
        return

    with open(db_filepath, "r", encoding="utf-8") as f:
        questions = json.load(f)

    total_count = len(questions)
    actual_end = total_count if end_idx is None or end_idx > total_count else end_idx
    
    print("==================================================")
    print("UniMock AI - Strict Gemini Embedding 2 Engine")
    print(f"Target Model: models/gemini-embedding-2 (3072 dims)")
    print(f"Pacing Delay: {pacing_delay}s/request (Max 90 RPM)")
    print(f"Database Path: {db_filepath}")
    print(f"Total Database Records: {total_count}")
    print(f"Processing Range: Index {start_idx} to {actual_end - 1} (Items {start_idx + 1} ~ {actual_end})")
    print("==================================================")

    skipped_count = 0
    processed_count = 0
    updated_count = 0

    for i in range(start_idx, actual_end):
        q_item = questions[i]
        q_id = q_item.get("id", f"q_{i+1:04d}")
        q_text = q_item.get("question", "")
        existing_vec = q_item.get("embedding")

        # Skip logic: If embedding already exists and is 3072-dim
        if existing_vec and isinstance(existing_vec, list) and len(existing_vec) == 3072 and not force_reembed:
            skipped_count += 1
            if skipped_count <= 3 or skipped_count % 200 == 0:
                print(f"[SKIP {q_id}] Already embedded (3072 dims).")
            continue

        try:
            # Compute 3072-dimensional vector embedding with automatic 100 RPM retry
            vec = embed_with_retry(q_text)
            q_item["embedding"] = vec
            processed_count += 1
            updated_count += 1

            if processed_count % 5 == 0 or i == actual_end - 1:
                safe_text = q_text[:20].encode("ascii", "ignore").decode("ascii") or "question_text"
                print(f"[EMBED {q_id}] Progress: [{i + 1}/{actual_end}] Computed 3072-dim vector for '{safe_text}...'")

            # Periodically save updated database every batch_save_interval items
            if updated_count % batch_save_interval == 0:
                with open(db_filepath, "w", encoding="utf-8") as f:
                    json.dump(questions, f, ensure_ascii=False, indent=2)
                print(f"--> [Checkpoint Saved] Disk updated with {updated_count} newly embedded items.")

            # Pacing delay to stay cleanly under 100 RPM limit
            if pacing_delay > 0:
                time.sleep(pacing_delay)

        except Exception as e:
            print(f"\n[ERROR at {q_id}] Stopped pre-embedding due to API Exception: {e}")
            print(f"Saving current progress before exiting...")
            if updated_count > 0:
                with open(db_filepath, "w", encoding="utf-8") as f:
                    json.dump(questions, f, ensure_ascii=False, indent=2)
            sys.exit(1)

    # Final save
    if updated_count > 0:
        with open(db_filepath, "w", encoding="utf-8") as f:
            json.dump(questions, f, ensure_ascii=False, indent=2)

    print("==================================================")
    print(f"Pre-embedding Finished Successfully!")
    print(f"- Total Examined: {actual_end - start_idx}")
    print(f"- Skipped (Already Embedded): {skipped_count}")
    print(f"- Newly Computed & Saved: {updated_count}")
    print(f"Database File: {db_filepath}")
    print("==================================================")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Strict Gemini Embedding 2 Pre-embedding Engine")
    parser.add_argument("--start", type=int, default=0, help="Start index (default: 0)")
    parser.add_argument("--end", type=int, default=None, help="End index (default: process all items)")
    parser.add_argument("--force", action="store_true", help="Force re-embedding of existing items")
    args = parser.parse_args()

    db_path = os.path.join(os.path.dirname(__file__), "..", "app", "db", "interview_questions_db.json")
    incremental_preembed(db_path, start_idx=args.start, end_idx=args.end, force_reembed=args.force)
