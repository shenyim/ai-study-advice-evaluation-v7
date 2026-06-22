import pandas as pd

from utils_paths import DATA_DIR, REPORTS_DIR, ensure_project_dirs, rel
from utils_reports import md_table, write_markdown


ANNOTATION_PATH = DATA_DIR / "human_annotation_merged.csv"
SAMPLE_PATH = DATA_DIR / "human_annotation_completed_sample.csv"
REPORT_PATH = REPORTS_DIR / "annotation_completeness_report.md"
SCORE_COLUMNS = ["usefulness_score", "specificity_score", "actionability_score", "empathy_score", "risk_control_score", "overall_score"]


def main() -> None:
    ensure_project_dirs()
    source = ANNOTATION_PATH if ANNOTATION_PATH.exists() else SAMPLE_PATH
    if not source.exists():
        write_markdown(REPORT_PATH, ["# Annotation Completeness Report", "", "No annotation file found yet."])
        print(f"WARNING: No annotation file found. Wrote {rel(REPORT_PATH)}")
        return

    df = pd.read_csv(source)
    for col in SCORE_COLUMNS:
        df[col] = pd.to_numeric(df.get(col), errors="coerce")
    missing_scores = int(df[SCORE_COLUMNS].isna().sum().sum())
    invalid_scores = int(((df[SCORE_COLUMNS] < 1) | (df[SCORE_COLUMNS] > 5)).sum().sum())

    model_coverage = df.groupby("model_name")["answer_id"].nunique().reset_index(name="annotated_answers")
    category_coverage = df.groupby("category")["answer_id"].nunique().reset_index(name="annotated_answers")
    rater_coverage = df.groupby("rater_id")["answer_id"].nunique().reset_index(name="annotated_answers")
    risk_coverage = df.groupby("risk_level")["answer_id"].nunique().reset_index(name="annotated_answers")

    lines = [
        "# Annotation Completeness Report",
        "",
        f"Source: `{rel(source)}`",
        "",
        "## Summary",
        "",
        f"- Number of answers annotated: **{df['answer_id'].nunique()}**",
        f"- Annotation rows: **{len(df)}**",
        f"- Missing scores: **{missing_scores}**",
        f"- Invalid scores outside 1-5: **{invalid_scores}**",
        "",
        "## Model Coverage",
        "",
        md_table(model_coverage),
        "",
        "## Category Coverage",
        "",
        md_table(category_coverage),
        "",
        "## Rater Coverage",
        "",
        md_table(rater_coverage),
        "",
        "## Risk-Level Coverage",
        "",
        md_table(risk_coverage),
    ]
    write_markdown(REPORT_PATH, lines)
    print(f"Wrote {rel(REPORT_PATH)}")


if __name__ == "__main__":
    main()

