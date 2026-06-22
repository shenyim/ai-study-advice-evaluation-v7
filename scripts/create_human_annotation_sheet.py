from pathlib import Path
import pandas as pd

BASE_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = BASE_DIR / "data"
DEFAULT_ANSWERS_PATH = DATA_DIR / "ai_answers.csv"
REAL_ANSWERS_PATH = DATA_DIR / "real_ai_answers_imported.csv"
QUESTIONS_PATH = DATA_DIR / "student_questions_clean.csv"
OUTPUT_PATH = DATA_DIR / "human_annotation_sheet.csv"
ANNOTATION_COLUMNS = ["rater_id", "accuracy", "helpfulness", "clarity", "actionability", "risk_control", "error_type", "confidence", "needs_review_manual", "notes"]

def main() -> None:
    if REAL_ANSWERS_PATH.exists():
        answers = pd.read_csv(REAL_ANSWERS_PATH)
    else:
        answers = pd.read_csv(DEFAULT_ANSWERS_PATH)
        if "answer_id" not in answers.columns:
            answers.insert(0, "answer_id", [f"A{i+1:04d}" for i in range(len(answers))])
        questions = pd.read_csv(QUESTIONS_PATH)
        answers = answers.merge(questions, on="question_id", how="left", validate="many_to_one")
    for col in ANNOTATION_COLUMNS:
        answers[col] = ""
    preferred_cols = ["answer_id", "question_id", "model_name", "category", "difficulty", "expected_risk", "student_background", "question_text", "answer_text"] + ANNOTATION_COLUMNS
    existing_cols = [col for col in preferred_cols if col in answers.columns]
    answers[existing_cols].to_csv(OUTPUT_PATH, index=False)
    print(f"Created annotation sheet with {len(answers)} rows -> {OUTPUT_PATH}")

if __name__ == "__main__":
    main()
