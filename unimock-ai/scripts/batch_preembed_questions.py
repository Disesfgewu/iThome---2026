import argparse
import json
import os
import sys

# Ensure root unimock-ai directory is in PYTHONPATH
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.services.embedding_service import embedding_service

def batch_preembed(db_filepath: str, start_idx: int, end_idx: int):
    """
    Pre-embeds questions in batches from start_idx to end_idx using Gemini Embedding 2 model.
    Saves pre-computed 768-dimensional float vectors directly into the JSON database.
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
    print(f"Target Processing Range: Item {start_idx + 1} to {actual_end} (Indices {start_idx}..{actual_end - 1})")
    print(f"==================================================")

    processed_count = 0
    for i in range(start_idx, actual_end):
        q_item = questions[i]
        q_text = q_item.get("question", "")

        # Compute vector embedding
        vec = embedding_service.embed_query(q_text)
        q_item["embedding"] = vec
        processed_count += 1

        if (processed_count % 100 == 0) or (i == actual_end - 1):
            print(f"Progress: [{processed_count}/{actual_end - start_idx}] Processed index {i} ('{q_text[:15]}...')")

    # Save updated database back to JSON
    with open(db_filepath, "w", encoding="utf-8") as f:
        json.dump(questions, f, ensure_ascii=False, indent=2)

    print(f"==================================================")
    print(f"Successfully pre-embedded {processed_count} items (Range: {start_idx + 1} ~ {actual_end}).")
    print(f"Updated database saved to: {db_filepath}")
    print(f"==================================================")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Batch Pre-embedding Script for UniMock AI Question Bank")
    parser.add_argument("--start", type=int, default=0, help="Start index (0-based, default 0 for 1st item)")
    parser.add_argument("--end", type=int, default=1000, help="End index (exclusive, default 1000 for 1000th item)")
    args = parser.parse_args()

    db_path = os.path.join(os.path.dirname(__file__), "..", "app", "db", "interview_questions_db.json")
    batch_preembed(db_path, args.start, args.end)
