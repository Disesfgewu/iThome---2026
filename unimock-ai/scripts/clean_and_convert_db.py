import json
import os

def strip_embeddings_from_db(json_filepath):
    """Resets interview_questions_db.json to clean state without any embedding vectors."""
    if not os.path.exists(json_filepath):
        print(f"Error: {json_filepath} not found!")
        return

    with open(json_filepath, "r", encoding="utf-8") as f:
        questions = json.load(f)

    cleaned_count = 0
    for q in questions:
        if "embedding" in q:
            del q["embedding"]
            cleaned_count += 1

    with open(json_filepath, "w", encoding="utf-8") as f:
        json.dump(questions, f, ensure_ascii=False, indent=2)

    print(f"[Reset DB] Successfully stripped embedding vectors from {cleaned_count} items in {json_filepath}.")
    print(f"[Reset DB] Total clean questions in database: {len(questions)}")

if __name__ == "__main__":
    json_path = os.path.join(os.path.dirname(__file__), "..", "app", "db", "interview_questions_db.json")
    strip_embeddings_from_db(json_path)
