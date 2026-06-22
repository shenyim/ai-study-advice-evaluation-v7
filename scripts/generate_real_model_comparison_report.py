import pandas as pd

from utils_paths import DATA_DIR, REPORTS_DIR, ensure_project_dirs, rel
from utils_reports import md_table, write_markdown


RATINGS_PATH = DATA_DIR / "ratings.csv"
REAL_PATH = DATA_DIR / "real_model_answers_clean.csv"
OUT_PATH = REPORTS_DIR / "real_model_comparison_report.md"


def main() -> None:
    ensure_project_dirs()
    if not REAL_PATH.exists():
        write_markdown(OUT_PATH, [
            "# Real Model Comparison Report",
            "",
            "Real model answers have not been imported yet. Run `python scripts/import_real_model_answers.py` after filling `data/real_model_answers_sample.csv` or replacing it with collected outputs.",
        ])
        print("WARNING: Real model data unavailable; wrote placeholder report.")
        return
    if not RATINGS_PATH.exists():
        write_markdown(OUT_PATH, ["# Real Model Comparison Report", "", "No scored ratings file found yet."])
        return

    df = pd.read_csv(RATINGS_PATH)
    real_ids = pd.read_csv(REAL_PATH)[["question_id", "model_name"]].drop_duplicates()
    df = df.merge(real_ids.assign(is_real=True), on=["question_id", "model_name"], how="inner")
    if df.empty:
        write_markdown(OUT_PATH, ["# Real Model Comparison Report", "", "Real answer rows exist, but no matching scored rows were found in `data/ratings.csv`."])
        return

    if "weighted_score" not in df.columns:
        df["weighted_score"] = df["overall_score"]
    if "needs_review" not in df.columns:
        df["needs_review"] = df["overall_score"] < 4
    if "review_priority" not in df.columns:
        df["review_priority"] = "none"
    if "error_type" not in df.columns and "failure_type" in df.columns:
        df["error_type"] = df["failure_type"]

    model = df.groupby("model_name").agg(
        answers=("question_id", "count"),
        unique_questions=("question_id", "nunique"),
        average_overall=("overall_score", "mean"),
        risk_weighted_score=("weighted_score", "mean"),
        review_rate=("needs_review", "mean"),
        p0_rate=("review_priority", lambda s: (s == "P0").mean()),
        p1_rate=("review_priority", lambda s: (s == "P1").mean()),
        p2_rate=("review_priority", lambda s: (s == "P2").mean()),
    ).reset_index()
    high = df[df["expected_risk"].eq("high")].groupby("model_name").agg(
        high_risk_answers=("question_id", "count"),
        high_risk_weighted=("weighted_score", "mean"),
        high_risk_review_rate=("needs_review", "mean"),
    ).reset_index()
    model = model.merge(high, on="model_name", how="left")
    numeric = model.select_dtypes(include="number").columns
    model[numeric] = model[numeric].round(3)
    failure_dist = pd.crosstab(df["model_name"], df.get("error_type", "none"), normalize="index").mul(100).round(1).reset_index()
    category_best = df.groupby(["category", "model_name"])["weighted_score"].mean().reset_index()
    category_best = category_best.sort_values(["category", "weighted_score"], ascending=[True, False]).groupby("category").head(1)
    worst = df.sort_values(["review_priority", "weighted_score", "overall_score"], ascending=[True, True, True]).head(10)

    best_model = model.sort_values(["risk_weighted_score", "review_rate"], ascending=[False, True]).iloc[0]["model_name"]
    p0_count = int((df["review_priority"] == "P0").sum())
    recommendation = (
        f"`{best_model}` is the strongest release candidate in this small real-output sample, but the recommendation is provisional."
        if p0_count == 0
        else "Do not treat any model as release-ready until open P0 cases are reviewed."
    )

    lines = [
        "# Real Model Comparison Report",
        "",
        "This report is generated only from imported real model answers that also have scores in the evaluation table.",
        "",
        "## Model-Level Results",
        "",
        md_table(model),
        "",
        "## Failure Type Distribution (%)",
        "",
        md_table(failure_dist),
        "",
        "## Best Model by Category",
        "",
        md_table(category_best.rename(columns={"weighted_score": "average_weighted_score"})),
        "",
        "## Worst Failure Cases",
        "",
        md_table(worst[["question_id", "model_name", "category", "expected_risk", "overall_score", "weighted_score", "review_priority", "error_type", "notes"] if "notes" in worst.columns else worst.columns.intersection(["question_id", "model_name", "category", "expected_risk", "overall_score", "weighted_score", "review_priority", "error_type"])]),
        "",
        "## Release Recommendation",
        "",
        recommendation,
        "",
        "## Limitations",
        "",
        "These results depend on sample size, rubric design, rater reliability, prompt setup, collection date, and model version. They should not be presented as a broad benchmark unless the dataset is expanded and the protocol is locked before collection.",
    ]
    write_markdown(OUT_PATH, lines)
    print(f"Wrote {rel(OUT_PATH)}")


if __name__ == "__main__":
    main()
