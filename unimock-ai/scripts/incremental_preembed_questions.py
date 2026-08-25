import argparse
import json
import os
import sys

# Ensure UTF-8 output encoding for Windows PowerShell / CMD
if sys.stdout and hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

# Ensure root unimock-ai directory is in PYTHONPATH
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.services.embedding_service import embedding_service

def incremental_preembed(db_filepath: str, start_idx: int = 0, end_idx: int = None, force_reembed: bool = False, batch_save_interval: int = 50):
    """
    Incremental Pre-embedding Script for UniMock AI.
    - Uses unique Question IDs (e.g., q_0001) for clear traceability.
    - Automatically detects and SKIPS questions that already have calculated embeddings.
    - Saves updated embeddings to JSON DB periodically every `batch_save_interval` items.
    """
    if not os.path.exists(db_filepath):
        print(f"Error: Database file {db_filepath} not found!")
        return

    with open(db_filepath, "r", encoding="utf-8") as f:
        questions = json.load(f)

    total_count = len(questions)
    actual_end = total_count if end_idx is None or end_idx > total_count else end_idx
    
    print("==================================================")
    print("UniMock AI - Incremental Vector Pre-embedding Engine")
    print(f"Database Path: {db_filepath}")
    print(f"Total Database Records: {total_count}")
    print(f"Processing Range: Index {start_idx} to {actual_end - 1} (Items {start_idx + 1} ~ {actual_end})")
    print(f"Force Re-embed Mode: {force_reembed}")
    print("==================================================")

    skipped_count = 0
    processed_count = 0
    updated_count = 0

    for i in range(start_idx, actual_end):
        q_item = questions[i]
        q_id = q_item.get("id", f"q_{i+1:04d}")
        q_text = q_item.get("question", "")
        existing_vec = q_item.get("embedding")

        # Skip logic: If embedding already exists and force_reembed is False
        if existing_vec and isinstance(existing_vec, list) and len(existing_vec) > 0 and not force_reembed:
            skipped_count += 1
            continue

        # Compute embedding for missing item
        vec = embedding_service.embed_query(q_text)
        q_item["embedding"] = vec
        processed_count += 1
        updated_count += 1

        if processed_count % 10 == 0 or i == actual_end - 1:
            safe_text = q_text[:20].encode("ascii", "ignore").decode("ascii") or "question_text"
            print(f"[EMBED {q_id}] Progress: [{processed_count}/{actual_end - start_idx - skipped_count}] Computed vector for '{safe_text}...'")

        # Periodically save updated database every batch_save_interval items
        if updated_count % batch_save_interval == 0:
            with open(db_filepath, "w", encoding="utf-8") as f:
                json.dump(questions, f, ensure_ascii=False, indent=2)
            print(f"--> Saved checkpoint to disk ({updated_count} newly embedded items saved).")

    # Final save
    if updated_count > 0:
        with open(db_filepath, "w", encoding="utf-8") as f:
            json.dump(questions, f, ensure_ascii=False, indent=2)

    print("==================================================")
    print(f"Incremental Pre-embedding Summary:")
    print(f"- Total Examined: {actual_end - start_idx}")
    print(f"- Skipped (Already Embedded): {skipped_count}")
    print(f"- Newly Computed & Saved: {updated_count}")
    print(f"Database File: {db_filepath}")
    print("==================================================")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Incremental Vector Pre-embedding Script")
    parser.add_argument("--start", type=int, default=0, help="Start index (default: 0)")
    parser.add_argument("--end", type=int, default=None, help="End index (default: process all items)")
    parser.add_argument("--force", action="store_true", help="Force re-embedding of existing items")
    args = parser.parse_args()

    db_path = os.path.join(os.path.dirname(__file__), "..", "app", "db", "interview_questions_db.json")
    incremental_preembed(db_path, start_idx=args.start, end_idx=args.end, force_reembed=args.force)
