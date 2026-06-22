from pathlib import Path

import pandas as pd

from utils_io import active_answer_input_path, load_evaluation_config, normalize_answer_columns

ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data"
QUESTIONS_PATH = DATA_DIR / "student_questions_clean.csv"
ANSWERS_PATH = DATA_DIR / "ai_answers.csv"
TEMPLATE_PATH = DATA_DIR / "ratings_template.csv"


def main() -> None:
    config = load_evaluation_config()
    questions = pd.read_csv(QUESTIONS_PATH)
    answer_path = active_answer_input_path()
    if not answer_path.exists():
        print(f"WARNING: {answer_path.relative_to(ROOT)} missing. Falling back to {ANSWERS_PATH.relative_to(ROOT)}.")
        answer_path = ANSWERS_PATH
    answers = normalize_answer_columns(pd.read_csv(answer_path))

    if config.get("mode") == "human_scored":
        answers.to_csv(TEMPLATE_PATH, index=False)
        print(f"Human-scored mode: copied {answer_path.relative_to(ROOT)} to {TEMPLATE_PATH.relative_to(ROOT)}")
        return

    df = answers.merge(questions, on="question_id", how="left", suffixes=("", "_question"))
    if "question_text" not in df.columns and "question_text_question" in df.columns:
        df["question_text"] = df["question_text_question"]
    if "expected_risk" not in df.columns and "expected_risk_question" in df.columns:
        df["expected_risk"] = df["expected_risk_question"]

    for col in ["accuracy", "helpfulness", "clarity", "actionability", "risk_control", "overall_score", "error_type", "notes"]:
        df[col] = ""

    columns = [
        "question_id",
        "category",
        "difficulty",
        "expected_risk",
        "student_background",
        "question_text",
        "model_name",
        "answer_text",
        "answer_length",
        "accuracy",
        "helpfulness",
        "clarity",
        "actionability",
        "risk_control",
        "overall_score",
        "error_type",
        "notes",
    ]

    df = df[columns]
    df.to_csv(TEMPLATE_PATH, index=False)

    print(f"{TEMPLATE_PATH.relative_to(ROOT)} created from {answer_path.relative_to(ROOT)}.")
    print("Rows:", df.shape[0])
    print(df[["question_id", "category", "expected_risk", "question_text"]].head())


if __name__ == "__main__":
    main()
