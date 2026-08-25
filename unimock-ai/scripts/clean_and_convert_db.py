import csv
import json
import os
import re

def clean_and_convert_csv_to_json(csv_filepath, output_json_filepath):
    print(f"Reading raw dataset from: {csv_filepath}")
    
    questions = []
    seen_questions = set()
    
    if not os.path.exists(csv_filepath):
        print(f"Error: {csv_filepath} not found!")
        return

    with open(csv_filepath, mode='r', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        idx = 1
        for row in reader:
            q_text = row.get("question", "").strip()
            if not q_text or q_text in seen_questions:
                continue
            
            seen_questions.add(q_text)
            
            school = row.get("school", "").strip() or "通用大學"
            dept_group = row.get("department_group", "").strip() or "資訊電機學群"
            dept = row.get("department", "").strip() or "資訊工程學系"
            q_type = row.get("question_type", "").strip() or "個人特質"
            school_tier = row.get("school_tier", "").strip() or "地區國立"
            dept_tags = [t.strip() for t in row.get("dept_tags", "").replace('"', '').split(",") if t.strip()]

            # Standardize reference answer and rubric
            ref_answer = row.get("reference_answer", "").strip()
            if not ref_answer or ref_answer == '""':
                ref_answer = f"針對【{dept}】之【{q_type}】問題，建議採用 STAR 原則（情境->任務->行動->成果）擬答，並結合備審專案經驗。"

            difficulty_label = "頂尖名校模式" if ("頂尖" in school_tier or "國立臺灣" in school or "成大" in school or "清大" in school) else "標準模擬模式"

            item = {
                "id": f"q_{idx:04d}",
                "school": school,
                "department_group": dept_group,
                "department": dept,
                "question_type": q_type,
                "question": q_text,
                "difficulty_mode": difficulty_label,
                "school_tier": school_tier,
                "dept_tags": dept_tags,
                "reference_answer": ref_answer,
                "rubric": {
                    "logic_structure": "評估是否採用 STAR 原則且條理清晰",
                    "major_relevance": "評估專業術語與學系契合度",
                    "communication_clarity": "評估口條流暢度與語速",
                    "adaptability": "評估面對追問的應變韌性"
                }
            }
            questions.append(item)
            idx += 1

    os.makedirs(os.path.dirname(output_json_filepath), exist_ok=True)
    with open(output_json_filepath, mode='w', encoding='utf-8') as f:
        json.dump(questions, f, ensure_ascii=False, indent=2)

    print(f"Successfully cleaned and saved {len(questions)} high-quality questions to: {output_json_filepath}")

if __name__ == "__main__":
    csv_path = os.path.join(os.path.dirname(__file__), "..", "datas", "interview_questions_rows.csv")
    json_path = os.path.join(os.path.dirname(__file__), "..", "app", "db", "interview_questions_db.json")
    clean_and_convert_csv_to_json(csv_path, json_path)
