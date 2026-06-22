import argparse
import math

import pandas as pd

from utils_io import active_answer_input_path, normalize_answer_columns
from utils_paths import DATA_DIR, ensure_project_dirs, rel


TEMPLATE_PATH = DATA_DIR / "human_annotation_template.csv"
SAMPLE_PATH = DATA_DIR / "human_annotation_completed_sample.csv"
SCORE_COLUMNS = [
    "usefulness_score",
    "specificity_score",
    "actionability_score",
    "empathy_score",
    "risk_control_score",
    "overall_score",
]


def build_annotation_frame() -> pd.DataFrame:
    answer_path = active_answer_input_path()
    if not answer_path.exists():
        answer_path = DATA_DIR / "ai_answers.csv"
    answers = normalize_answer_columns(pd.read_csv(answer_path))
    questions_path = DATA_DIR / "student_questions_clean.csv"
    if questions_path.exists():
        questions = pd.read_csv(questions_path)
        answers = answers.merge(questions, on="question_id", how="left", suffixes=("", "_question"))

    for source, target in [("question_text_question", "question_text"), ("expected_risk_question", "expected_risk")]:
        if target not in answers.columns and source in answers.columns:
            answers[target] = answers[source]

    base = pd.DataFrame({
        "answer_id": answers.get("answer_id", answers["question_id"].astype(str) + "__" + answers["model_name"].astype(str)),
        "question_id": answers["question_id"],
        "model_name": answers["model_name"],
        "category": answers.get("category", ""),
        "risk_level": answers.get("expected_risk", answers.get("risk_level", "")),
        "student_question": answers.get("question_text", answers.get("student_question", "")),
        "answer_text": answers["answer_text"],
    })
    for col in SCORE_COLUMNS:
        base[col] = ""
    base["failure_type"] = ""
    base["reviewer_notes"] = ""
    base["rater_id"] = ""
    return base


def create_completed_sample(template: pd.DataFrame) -> pd.DataFrame:
    sample = template.head(min(18, len(template))).copy()
    if sample.empty:
        return sample
    rows = []
    raters = ["R1", "R2"]
    for _, row in sample.iterrows():
        for rater in raters:
            new = row.copy()
            seed = sum(ord(ch) for ch in f"{row['answer_id']}-{rater}")
            base = 3.7 + (seed % 8) * 0.15
            for i, col in enumerate(SCORE_COLUMNS[:-1]):
                new[col] = round(max(1, min(5, base + ((seed + i) % 3 - 1) * 0.25)), 1)
            new["overall_score"] = round(sum(float(new[col]) for col in SCORE_COLUMNS[:-1]) / 5, 2)
            new["failure_type"] = "none" if new["overall_score"] >= 4 else "missing_steps"
            new["reviewer_notes"] = "Completed sample rating for workflow demonstration."
            new["rater_id"] = rater
            rows.append(new)
    return pd.DataFrame(rows)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--raters", default="R1,R2", help="Comma-separated rater IDs for batch files.")
    parser.add_argument("--batch-size", type=int, default=40)
    args = parser.parse_args()

    ensure_project_dirs()
    template = build_annotation_frame()
    template.to_csv(TEMPLATE_PATH, index=False)
    sample = create_completed_sample(template)
    sample.to_csv(SAMPLE_PATH, index=False)

    raters = [r.strip() for r in args.raters.split(",") if r.strip()]
    for rater in raters:
        rater_dir = DATA_DIR / "annotation_batches"
        rater_dir.mkdir(exist_ok=True)
        total_batches = max(1, math.ceil(len(template) / args.batch_size))
        for batch_num in range(total_batches):
            batch = template.iloc[batch_num * args.batch_size : (batch_num + 1) * args.batch_size].copy()
            batch["rater_id"] = rater
            batch.to_csv(rater_dir / f"annotation_batch_{rater}_{batch_num + 1:02d}.csv", index=False)

    print(f"Wrote {rel(TEMPLATE_PATH)}")
    print(f"Wrote {rel(SAMPLE_PATH)}")


if __name__ == "__main__":
    main()

