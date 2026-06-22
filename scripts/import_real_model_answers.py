import pandas as pd

from utils_paths import DATA_DIR, REPORTS_DIR, ensure_project_dirs, rel
from utils_reports import write_markdown
from validate_real_model_answers import REQUIRED_COLUMNS, SOURCE_PATH, validate


CLEAN_PATH = DATA_DIR / "real_model_answers_clean.csv"
REPORT_PATH = REPORTS_DIR / "real_model_validation_report.md"


def main() -> None:
    ensure_project_dirs()
    df, issues, metrics = validate(SOURCE_PATH)
    if df.empty:
        print("WARNING: No real model answers found. Simulated mode can still run.")
        write_markdown(REPORT_PATH, ["# Real Model Validation Report", "", f"Missing or empty input: `{rel(SOURCE_PATH)}`"])
        return

    clean = df.copy()
    clean = clean.drop_duplicates(subset=["question_id", "model_name"], keep="first")
    clean = clean[clean["answer_text"].fillna("").astype(str).str.split().str.len() >= 20].copy()
    clean["expected_risk"] = clean["risk_level"].str.lower()
    clean["question_text"] = clean["student_question"]
    clean["answer_id"] = clean["question_id"].astype(str) + "__" + clean["model_name"].astype(str)
    clean["answer_length"] = clean["answer_text"].str.split().str.len()
    clean.to_csv(CLEAN_PATH, index=False)

    lines = [
        "# Real Model Validation Report",
        "",
        f"Input checked: `{rel(SOURCE_PATH)}`",
        f"Clean output: `{rel(CLEAN_PATH)}`",
        "",
        "## Summary",
        "",
    ]
    for key, value in metrics.items():
        lines.append(f"- {key.replace('_', ' ').title()}: **{value}**")
    lines += [
        f"- Rows retained after cleaning: **{len(clean)}**",
        "",
        "## Issues",
        "",
    ]
    lines += [f"- {issue}" for issue in issues] if issues else ["- No blocking issues found."]
    lines += [
        "",
        "## Notes",
        "",
        "The importer standardizes `risk_level` to `expected_risk`, `student_question` to `question_text`, and creates `answer_id` from `question_id + model_name`.",
    ]
    write_markdown(REPORT_PATH, lines)
    print(f"Imported {len(clean)} rows to {rel(CLEAN_PATH)}")


if __name__ == "__main__":
    main()

