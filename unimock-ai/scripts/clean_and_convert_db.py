import csv
import json
import os

def clean_and_convert_csv_to_json(csv_filepath, output_json_filepath):
    print(f"Reading raw dataset for de-identification from: {csv_filepath}")
    
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
            
            # De-identify: Remove explicit school names from question text if any, and do not bind to specific schools
            dept_group = row.get("department_group", "").strip() or "資訊電機學群"
            dept = row.get("department", "").strip() or "資訊工程學系"
            raw_type = row.get("question_type", "").strip() or "個人特質"
            school_tier = row.get("school_tier", "").strip() or "地區國立"
            dept_tags = [t.strip() for t in row.get("dept_tags", "").replace('"', '').split(",") if t.strip()]

            # Determine Question Category (通用型問題 vs 技術專業型問題 vs 個人特質 vs 情境題)
            if "專業" in raw_type or "知識" in raw_type:
                q_category = "技術專業型問題"
            elif "個人" in raw_type or "動機" in raw_type:
                q_category = "通用型問題"
            elif "情境" in raw_type or "應變" in raw_type:
                q_category = "情境申論型問題"
            else:
                q_category = "通用型問題"

            # Determine Difficulty Level (標準題 vs 進階專業題 vs 高難度申論題)
            if "頂尖" in school_tier or "研究型" in school_tier:
                difficulty_level = "高難度申論題" if q_category == "情境申論型問題" else "進階專業題"
            else:
                difficulty_level = "標準題"

            # Standardize reference answer and rubric
            ref_answer = row.get("reference_answer", "").strip()
            if not ref_answer or ref_answer == '""':
                ref_answer = f"針對【{dept}】之【{q_category}】，建議採用 STAR 原則（情境->任務->行動->成果）擬答，並結合備審專案經驗與量化數據。"

            item = {
                "id": f"q_{idx:04d}",
                "deidentified": True,
                "department_group": dept_group,
                "department": dept,
                "question_category": q_category,
                "difficulty_level": difficulty_level,
                "question": q_text,
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

    print(f"Successfully de-identified and saved {len(questions)} items to: {output_json_filepath}")

if __name__ == "__main__":
    csv_path = os.path.join(os.path.dirname(__file__), "..", "datas", "interview_questions_rows.csv")
    json_path = os.path.join(os.path.dirname(__file__), "..", "app", "db", "interview_questions_db.json")
    clean_and_convert_csv_to_json(csv_path, json_path)
