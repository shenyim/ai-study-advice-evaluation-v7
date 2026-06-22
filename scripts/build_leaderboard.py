from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data"
REPORTS_DIR = ROOT / "reports"
RATINGS_PATH = DATA_DIR / "ratings.csv"
OUT_CSV = REPORTS_DIR / "model_leaderboard.csv"
OUT_MD = REPORTS_DIR / "model_leaderboard.md"
SCORE_COLS = ["accuracy", "helpfulness", "clarity", "actionability", "risk_control"]


def main() -> None:
    REPORTS_DIR.mkdir(exist_ok=True)
    df = pd.read_csv(RATINGS_PATH)
    if "weighted_score" not in df.columns:
        df["weighted_score"] = df.get("overall_score")
    if "needs_review" not in df.columns:
        df["needs_review"] = df["quality_status"].eq("review") if "quality_status" in df.columns else df["overall_score"] < 4.0
    if "review_priority" not in df.columns:
        df["review_priority"] = "none"

    summary = df.groupby("model_name").agg(
        evaluated_answers=("question_id", "count"),
        unique_questions=("question_id", "nunique"),
        overall_score=("overall_score", "mean"),
        weighted_score=("weighted_score", "mean"),
        review_rate=("needs_review", "mean"),
        p0_rate=("review_priority", lambda s: (s == "P0").mean()),
        high_risk_coverage=("expected_risk", lambda s: (s == "high").sum()),
    ).reset_index()
    for col in SCORE_COLS:
        summary[col] = df.groupby("model_name")[col].mean().values
    summary["release_candidate_score"] = (
        summary["weighted_score"] * 0.55
        + summary["risk_control"] * 0.20
        + (1 - summary["review_rate"]) * 5 * 0.15
        + (1 - summary["p0_rate"]) * 5 * 0.10
    )
    summary = summary.sort_values("release_candidate_score", ascending=False)
    numeric_cols = summary.select_dtypes(include="number").columns
    summary[numeric_cols] = summary[numeric_cols].round(3)
    summary.to_csv(OUT_CSV, index=False)

    best = summary.iloc[0]
    lines = [
        "# Model Leaderboard",
        "",
        "This leaderboard combines answer quality, risk control, review workload, and P0 safety pressure.",
        "",
        f"Recommended release candidate for the current demo dataset: **{best['model_name']}**.",
        "",
        "| Rank | Model | Release Candidate Score | Risk-weighted | Review Rate | P0 Rate |",
        "|---:|---|---:|---:|---:|---:|",
    ]
    for rank, (_, row) in enumerate(summary.iterrows(), start=1):
        lines.append(
            f"| {rank} | {row['model_name']} | {row['release_candidate_score']:.2f} | {row['weighted_score']:.2f} | {row['review_rate']:.1%} | {row['p0_rate']:.1%} |"
        )
    lines += [
        "",
        "## Interpretation",
        "",
        "Use this as a product-selection artifact, not as proof that any real commercial model is better. The current values come from the simulated demo dataset unless real model outputs and human ratings are connected.",
    ]
    OUT_MD.write_text("\n".join(lines), encoding="utf-8")
    print(f"Created {OUT_CSV.relative_to(ROOT)} and {OUT_MD.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
