from pathlib import Path

import pandas as pd

from utils_paths import DATA_DIR, REPORTS_DIR, ensure_project_dirs, rel
from utils_reports import write_markdown


BATCH_DIR = DATA_DIR / "annotation_batches"
SAMPLE_PATH = DATA_DIR / "human_annotation_completed_sample.csv"
OUT_PATH = DATA_DIR / "human_annotation_merged.csv"
HUMAN_SCORED_PATH = DATA_DIR / "human_scored_answers.csv"
REPORT_PATH = REPORTS_DIR / "annotation_merge_report.md"
SCORE_COLUMNS = ["usefulness_score", "specificity_score", "actionability_score", "empathy_score", "risk_control_score", "overall_score"]


def annotation_files() -> list[Path]:
    files = sorted(BATCH_DIR.glob("*.csv")) if BATCH_DIR.exists() else []
    completed = [f for f in files if "completed" in f.name.lower()]
    return completed or ([SAMPLE_PATH] if SAMPLE_PATH.exists() else [])


def main() -> None:
    ensure_project_dirs()
    files = annotation_files()
    if not files:
        print("WARNING: No completed annotation files found.")
        write_markdown(REPORT_PATH, ["# Annotation Merge Report", "", "No completed annotation files were found."])
        return

    frames = [pd.read_csv(path) for path in files]
    merged = pd.concat(frames, ignore_index=True)
    for col in SCORE_COLUMNS:
        merged[col] = pd.to_numeric(merged.get(col), errors="coerce")
    merged.to_csv(OUT_PATH, index=False)

    score_map = {
        "usefulness_score": "helpfulness",
        "specificity_score": "clarity",
        "actionability_score": "actionability",
        "empathy_score": "accuracy",
        "risk_control_score": "risk_control",
    }
    human = merged.groupby(["answer_id", "question_id", "model_name"], dropna=False).agg(
        category=("category", "first"),
        expected_risk=("risk_level", "first"),
        question_text=("student_question", "first"),
        answer_text=("answer_text", "first"),
        usefulness_score=("usefulness_score", "mean"),
        specificity_score=("specificity_score", "mean"),
        actionability_score=("actionability_score", "mean"),
        empathy_score=("empathy_score", "mean"),
        risk_control_score=("risk_control_score", "mean"),
        overall_score=("overall_score", "mean"),
        failure_type=("failure_type", lambda s: s.mode().iloc[0] if not s.mode().empty else "none"),
        notes=("reviewer_notes", lambda s: " | ".join(sorted(set(s.dropna().astype(str)))[:3])),
    ).reset_index()
    for old, new in score_map.items():
        human[new] = human[old].round(2)
    human["overall_score"] = human["overall_score"].round(2)
    human["error_type"] = human["failure_type"]
    human["answer_length"] = human["answer_text"].fillna("").astype(str).str.split().str.len()
    human.to_csv(HUMAN_SCORED_PATH, index=False)

    lines = [
        "# Annotation Merge Report",
        "",
        f"Files merged: **{len(files)}**",
        f"Annotation rows: **{len(merged)}**",
        f"Unique answers: **{merged['answer_id'].nunique()}**",
        f"Human-scored output: `{rel(HUMAN_SCORED_PATH)}`",
    ]
    write_markdown(REPORT_PATH, lines)
    print(f"Wrote {rel(OUT_PATH)}")
    print(f"Wrote {rel(HUMAN_SCORED_PATH)}")


if __name__ == "__main__":
    main()

