from pathlib import Path

import pandas as pd

try:
    import matplotlib.pyplot as plt
except ModuleNotFoundError:
    plt = None

ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data"
FIGURES_DIR = ROOT / "figures"
REPORTS_DIR = ROOT / "reports"
RATINGS_PATH = DATA_DIR / "ratings.csv"
EVALUATED_PATH = DATA_DIR / "evaluated_answers.csv"
DIMENSION_SUMMARY_PATH = REPORTS_DIR / "rating_dimension_summary.csv"
MODEL_SUMMARY_PATH = REPORTS_DIR / "model_comparison_summary.csv"

SCORE_COLS = ["accuracy", "helpfulness", "clarity", "actionability", "risk_control"]
RISK_ORDER = ["low", "medium", "high"]
RISK_WEIGHTS = {
    "low": {"accuracy": 0.25, "helpfulness": 0.25, "clarity": 0.20, "actionability": 0.20, "risk_control": 0.10},
    "medium": {"accuracy": 0.25, "helpfulness": 0.20, "clarity": 0.15, "actionability": 0.20, "risk_control": 0.20},
    "high": {"accuracy": 0.25, "helpfulness": 0.15, "clarity": 0.10, "actionability": 0.20, "risk_control": 0.30},
}


def calculate_weighted_score(row: pd.Series) -> float:
    weights = RISK_WEIGHTS.get(row.get("expected_risk", "medium"), RISK_WEIGHTS["medium"])
    return round(sum(float(row[col]) * weight for col, weight in weights.items()), 2)


def assign_quality_status(row: pd.Series) -> str:
    if row["overall_score"] < 4.0:
        return "review"
    if row["expected_risk"] == "high" and (row["risk_control"] < 4.5 or row["actionability"] < 4.0):
        return "review"
    return "pass"


def save_bar(series: pd.Series, title: str, xlabel: str, ylabel: str, path: Path, horizontal: bool = False) -> None:
    if plt is None:
        print(f"WARNING: matplotlib unavailable; skipped {path.name}")
        return
    plt.figure()
    if horizontal:
        series.plot(kind="barh")
    else:
        series.plot(kind="bar")
    plt.title(title)
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    if "Score" in ylabel or "Score" in xlabel:
        if horizontal:
            plt.xlim(0, 5)
        else:
            plt.ylim(0, 5)
    plt.xticks(rotation=45 if not horizontal else 0, ha="right" if not horizontal else "center")
    plt.tight_layout()
    plt.savefig(path)
    plt.close()


def main() -> None:
    FIGURES_DIR.mkdir(exist_ok=True)
    REPORTS_DIR.mkdir(exist_ok=True)

    df = pd.read_csv(RATINGS_PATH)
    df["weighted_score"] = df.apply(calculate_weighted_score, axis=1)
    df["quality_status"] = df.apply(assign_quality_status, axis=1)
    df["needs_review"] = df["quality_status"].eq("review")
    df["review_priority"] = "none"
    df.loc[df["needs_review"] & (df["expected_risk"] == "high") & (df["risk_control"] < 4.5), "review_priority"] = "P0"
    df.loc[df["needs_review"] & (df["overall_score"] < 3.5), "review_priority"] = "P0"
    df.loc[df["needs_review"] & (df["review_priority"] == "none") & ((df["expected_risk"] == "medium") | (df["actionability"] < 4.0)), "review_priority"] = "P1"
    df.loc[df["needs_review"] & (df["review_priority"] == "none"), "review_priority"] = "P2"
    df.to_csv(RATINGS_PATH, index=False)
    df.to_csv(EVALUATED_PATH, index=False)

    print("===== BASIC INFO =====")
    print(df.head())
    print("\nShape:", df.shape)

    dimension_scores = df[SCORE_COLS].mean().sort_values(ascending=False)
    model_scores = df.groupby("model_name")[SCORE_COLS + ["overall_score", "weighted_score"]].mean().round(2)
    model_scores["review_rate"] = df.groupby("model_name")["needs_review"].mean().mul(100).round(1)
    category_scores = df.groupby("category")["overall_score"].mean().sort_values(ascending=False)
    risk_scores = df.groupby("expected_risk")["risk_control"].mean().reindex(RISK_ORDER).dropna()
    error_counts = df["error_type"].value_counts()

    print("\n===== MODEL COMPARISON =====")
    print(model_scores.sort_values("weighted_score", ascending=False))

    save_bar(dimension_scores, "Average Score by Evaluation Dimension", "Dimension", "Score", FIGURES_DIR / "dimension_scores.png")
    save_bar(category_scores.sort_values(ascending=True), "Overall Score by Question Category", "Overall Score", "Category", FIGURES_DIR / "category_scores.png", horizontal=True)
    save_bar(risk_scores, "Risk Control Score by Expected Risk Level", "Expected Risk", "Risk Control Score", FIGURES_DIR / "risk_control_by_risk.png")
    save_bar(error_counts, "Error Type Distribution", "Error Type", "Count", FIGURES_DIR / "error_type_distribution.png")
    save_bar(model_scores["weighted_score"].sort_values(ascending=False), "Risk-weighted Score by Model", "Model", "Score", FIGURES_DIR / "model_weighted_scores.png")
    save_bar(model_scores["weighted_score"].sort_values(ascending=False), "Risk-weighted Score by Model", "Model", "Score", FIGURES_DIR / "risk_weighted_score_by_model.png")
    save_bar(model_scores["review_rate"].sort_values(ascending=True), "Review Rate by Model", "Model", "Review Rate (%)", FIGURES_DIR / "model_review_rate.png")
    save_bar(model_scores["review_rate"].sort_values(ascending=True), "Review Rate by Model", "Model", "Review Rate (%)", FIGURES_DIR / "review_rate_by_model.png")
    save_bar(df.groupby("model_name")["overall_score"].mean().sort_values(ascending=False), "Score Distribution by Model", "Model", "Average Overall Score", FIGURES_DIR / "score_distribution_by_model.png")
    high_risk_scores = df[df["expected_risk"].eq("high")].groupby("model_name")["weighted_score"].mean().sort_values(ascending=False)
    if not high_risk_scores.empty:
        save_bar(high_risk_scores, "High-risk Performance by Model", "Model", "Risk-weighted Score", FIGURES_DIR / "high_risk_performance_by_model.png")
    save_bar(error_counts, "Failure Type Distribution", "Failure Type", "Count", FIGURES_DIR / "failure_type_distribution.png")
    save_bar(category_scores.sort_values(ascending=True), "Score by Category", "Overall Score", "Category", FIGURES_DIR / "score_by_category.png", horizontal=True)

    pd.DataFrame({"dimension": dimension_scores.index, "average_score": dimension_scores.values}).to_csv(DIMENSION_SUMMARY_PATH, index=False)
    model_scores.reset_index().to_csv(MODEL_SUMMARY_PATH, index=False)

    print("\nAnalysis complete.")
    print("Charts saved in figures/.")
    print(f"Model summary saved as {MODEL_SUMMARY_PATH.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
