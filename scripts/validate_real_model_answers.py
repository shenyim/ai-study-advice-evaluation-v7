import pandas as pd

from utils_paths import DATA_DIR, REPORTS_DIR, ensure_project_dirs, rel
from utils_reports import write_markdown


REQUIRED_COLUMNS = [
    "question_id",
    "category",
    "risk_level",
    "student_question",
    "model_name",
    "model_version",
    "prompt_version",
    "answer_text",
    "collection_date",
    "collector_notes",
]

SOURCE_PATH = DATA_DIR / "real_model_answers_sample.csv"
TEMPLATE_PATH = DATA_DIR / "real_model_answers_template.csv"
REPORT_PATH = REPORTS_DIR / "real_model_validation_report.md"


def validate(path=SOURCE_PATH) -> tuple[pd.DataFrame, list[str], dict]:
    if not path.exists():
        return pd.DataFrame(columns=REQUIRED_COLUMNS), [f"Missing input file: {rel(path)}"], {}

    df = pd.read_csv(path)
    issues = []
    missing_cols = [col for col in REQUIRED_COLUMNS if col not in df.columns]
    if missing_cols:
        issues.append(f"Missing required columns: {', '.join(missing_cols)}")
        for col in missing_cols:
            df[col] = pd.NA

    df = df[REQUIRED_COLUMNS].copy()
    text_cols = ["question_id", "category", "risk_level", "student_question", "model_name", "model_version", "prompt_version", "answer_text", "collection_date", "collector_notes"]
    for col in text_cols:
        df[col] = df[col].fillna("").astype(str).str.strip()

    df["answer_word_count"] = df["answer_text"].str.split().str.len()
    missing_answers = int(df["answer_text"].eq("").sum())
    duplicate_pairs = int(df.duplicated(subset=["question_id", "model_name"], keep=False).sum())
    too_short = int((df["answer_word_count"] < 20).sum())
    invalid_risk = sorted(set(df.loc[~df["risk_level"].isin(["low", "medium", "high"]), "risk_level"]) - {""})

    if missing_answers:
        issues.append(f"Missing answers: {missing_answers}")
    if duplicate_pairs:
        issues.append(f"Duplicate question_id + model_name rows: {duplicate_pairs}")
    if too_short:
        issues.append(f"Answers below 20 words: {too_short}")
    if invalid_risk:
        issues.append(f"Unexpected risk levels: {', '.join(invalid_risk)}")

    metrics = {
        "rows": len(df),
        "unique_questions": df["question_id"].nunique(),
        "models": df["model_name"].nunique(),
        "missing_answers": missing_answers,
        "duplicate_question_model_pairs": duplicate_pairs,
        "too_short_answers": too_short,
    }
    return df, issues, metrics


def main() -> None:
    ensure_project_dirs()
    if not TEMPLATE_PATH.exists():
        pd.DataFrame(columns=REQUIRED_COLUMNS).to_csv(TEMPLATE_PATH, index=False)

    df, issues, metrics = validate()
    lines = [
        "# Real Model Validation Report",
        "",
        f"Input checked: `{rel(SOURCE_PATH)}`",
        "",
        "## Summary",
        "",
    ]
    if metrics:
        for key, value in metrics.items():
            lines.append(f"- {key.replace('_', ' ').title()}: **{value}**")
    else:
        lines.append("- No real model rows were available.")
    lines += ["", "## Issues", ""]
    lines += [f"- {issue}" for issue in issues] if issues else ["- No blocking issues found."]
    lines += [
        "",
        "## Required Columns",
        "",
        ", ".join(f"`{col}`" for col in REQUIRED_COLUMNS),
    ]
    write_markdown(REPORT_PATH, lines)
    print(f"Checked {rel(SOURCE_PATH)}")
    print(f"Wrote {rel(REPORT_PATH)}")


if __name__ == "__main__":
    main()

