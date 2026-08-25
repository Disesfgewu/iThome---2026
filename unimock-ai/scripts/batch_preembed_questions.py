import argparse
import json
import os
import sys

# Ensure root unimock-ai directory is in PYTHONPATH
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.services.embedding_service import embedding_service

def batch_preembed(db_filepath: str, start_idx: int, end_idx: int, skip_existing: bool = True):
    """
    Pre-embeds questions in batches from start_idx to end_idx using Gemini Embedding 2 model.
    Saves pre-computed 768-dimensional float vectors directly into the JSON database.
    Skips items that already have computed vectors when skip_existing=True.
    """
    if not os.path.exists(db_filepath):
        print(f"Error: Database file {db_filepath} not found!")
        return

    with open(db_filepath, "r", encoding="utf-8") as f:
        questions = json.load(f)

    total_count = len(questions)
    actual_end = min(end_idx, total_count)
    
    print(f"==================================================")
    print(f"Starting Batch Pre-embedding with Gemini Embedding 2")
    print(f"DB Path: {db_filepath}")
    print(f"Total Questions: {total_count}")
    print(f"Processing Range: ID {questions[start_idx].get('id', 'N/A')} (Index {start_idx}) to ID {questions[actual_end - 1].get('id', 'N/A')} (Index {actual_end - 1})")
    print(f"Skip Existing Mode: {skip_existing}")
    print(f"==================================================")

    processed_count = 0
    skipped_count = 0

    for i in range(start_idx, actual_end):
        q_item = questions[i]
        q_id = q_item.get("id", f"q_{i+1:04d}")
        q_text = q_item.get("question", "")

        # Skip if already embedded
        if skip_existing and q_item.get("embedding"):
            skipped_count += 1
            continue

        # Compute vector embedding
        vec = embedding_service.embed_query(q_text)
        q_item["embedding"] = vec
        processed_count += 1

        if (processed_count % 50 == 0) or (i == actual_end - 1):
            print(f"Progress: [{processed_count} computed, {skipped_count} skipped] Processed [{q_id}] ('{q_text[:15]}...')")

    # Save updated database back to JSON
    with open(db_filepath, "w", encoding="utf-8") as f:
        json.dump(questions, f, ensure_ascii=False, indent=2)

    print(f"==================================================")
    print(f"Batch Summary: {processed_count} newly embedded, {skipped_count} skipped.")
    print(f"Updated database saved to: {db_filepath}")
    print(f"==================================================")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Batch Pre-embedding Script for UniMock AI Question Bank")
    parser.add_argument("--start", type=int, default=0, help="Start index (0-based)")
    parser.add_argument("--end", type=int, default=1000, help="End index (exclusive)")
    parser.add_argument("--force", action="store_true", help="Force re-embedding even if vectors exist")
    args = parser.parse_args()

    db_path = os.path.join(os.path.dirname(__file__), "..", "app", "db", "interview_questions_db.json")
    batch_preembed(db_path, args.start, args.end, skip_existing=not args.force)
