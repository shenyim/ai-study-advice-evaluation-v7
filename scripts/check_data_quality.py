from pathlib import Path
import pandas as pd

BASE_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = BASE_DIR / "data"
REPORT_PATH = BASE_DIR / "reports" / "data_quality_report.md"
RATINGS_PATH = DATA_DIR / "ratings.csv"
SCORE_COLS = ["accuracy", "helpfulness", "clarity", "actionability", "risk_control", "overall_score"]
VALID_RISK = {"low", "medium", "high"}

def pct(x: float) -> str:
    return f"{x * 100:.1f}%"

def main() -> None:
    df = pd.read_csv(RATINGS_PATH)
    issues = []
    duplicate_answers = df["answer_id"].duplicated().sum() if "answer_id" in df.columns else 0
    if duplicate_answers:
        issues.append(f"Duplicate answer_id rows: {duplicate_answers}")
    for col in SCORE_COLS:
        if col in df.columns:
            numeric = pd.to_numeric(df[col], errors="coerce")
            invalid = numeric.isna().sum()
            out_of_range = (~numeric.between(1, 5)).sum()
            if invalid or out_of_range:
                issues.append(f"{col}: {invalid} non-numeric values; {out_of_range} values outside 1-5")
    if "expected_risk" in df.columns:
        risks = set(df["expected_risk"].dropna().astype(str).str.lower().unique())
        unknown = sorted(risks - VALID_RISK)
        if unknown:
            issues.append(f"Unknown expected_risk values: {unknown}")
    coverage = df.groupby("model_name")["question_id"].nunique().sort_values(ascending=False) if "model_name" in df.columns else pd.Series(dtype=int)
    review_text = "Not available"
    if "needs_review" in df.columns:
        review_text = pct(df["needs_review"].astype(bool).mean())
    lines = ["# Data Quality Report", "", "This report checks whether the current evaluation dataset is ready for product or research analysis.", "", "## Dataset Snapshot", f"- Rows: {len(df)}", f"- Unique questions: {df['question_id'].nunique() if 'question_id' in df.columns else 'N/A'}", f"- Unique models: {df['model_name'].nunique() if 'model_name' in df.columns else 'N/A'}", f"- Review rate: {review_text}", "", "## Model Coverage"]
    if coverage.empty:
        lines.append("- Model coverage could not be computed.")
    else:
        for model, count in coverage.items():
            lines.append(f"- {model}: {count} questions")
    lines += ["", "## Issues"]
    if issues:
        lines.extend(f"- {issue}" for issue in issues)
    else:
        lines.append("- No blocking data quality issues found.")
    lines += ["", "## Recommended Next Checks", "- Add at least two human raters for a subset of answers.", "- Track prompt version and model version for every answer.", "- Separate simulated answers from real model outputs before making external claims.", "- Use high-risk questions as the main regression test set when changing prompts or models."]
    REPORT_PATH.write_text("\n".join(lines), encoding="utf-8")
    print(f"Wrote {REPORT_PATH}")

if __name__ == "__main__":
    main()
