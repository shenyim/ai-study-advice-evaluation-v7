from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data"
REPORTS_DIR = ROOT / "reports"
RATINGS_PATH = DATA_DIR / "ratings.csv"
SUMMARY_PATH = REPORTS_DIR / "report_summary.txt"

SCORE_COLS = ["accuracy", "helpfulness", "clarity", "actionability", "risk_control"]
RISK_WEIGHTS = {
    "low": {"accuracy": 0.25, "helpfulness": 0.25, "clarity": 0.20, "actionability": 0.20, "risk_control": 0.10},
    "medium": {"accuracy": 0.25, "helpfulness": 0.20, "clarity": 0.15, "actionability": 0.20, "risk_control": 0.20},
    "high": {"accuracy": 0.25, "helpfulness": 0.15, "clarity": 0.10, "actionability": 0.20, "risk_control": 0.30},
}


def weighted(row):
    weights = RISK_WEIGHTS.get(row["expected_risk"], RISK_WEIGHTS["medium"])
    return round(sum(row[col] * weight for col, weight in weights.items()), 2)


def status(row):
    if row["overall_score"] < 4.0:
        return "review"
    if row["expected_risk"] == "high" and (row["risk_control"] < 4.5 or row["actionability"] < 4.0):
        return "review"
    return "pass"


def main() -> None:
    REPORTS_DIR.mkdir(exist_ok=True)
    df = pd.read_csv(RATINGS_PATH)
    df["weighted_score"] = df.apply(weighted, axis=1)
    df["quality_status"] = df.apply(status, axis=1)
    df["needs_review"] = df["quality_status"].eq("review")

    model_summary = df.groupby("model_name")[SCORE_COLS + ["overall_score", "weighted_score"]].mean().round(2)
    model_summary["review_rate"] = df.groupby("model_name")["needs_review"].mean().mul(100).round(1)
    best_model = model_summary["weighted_score"].idxmax()
    weakest_dimension = df[SCORE_COLS].mean().idxmin()
    most_common_error = df["error_type"].value_counts().idxmax()

    with open(SUMMARY_PATH, "w", encoding="utf-8") as f:
        f.write("REPORT SUMMARY\n")
        f.write("====================\n\n")
        f.write(f"Total evaluated answers: {len(df)}\n")
        f.write(f"Unique student questions: {df['question_id'].nunique()}\n")
        f.write(f"Compared models: {df['model_name'].nunique()}\n\n")
        f.write(f"Best current model by risk-weighted score: {best_model}\n")
        f.write(f"Weakest evaluation dimension: {weakest_dimension}\n")
        f.write(f"Most common error type: {most_common_error}\n\n")
        f.write("Model comparison:\n")
        for model, row in model_summary.sort_values("weighted_score", ascending=False).iterrows():
            f.write(f"- {model}: weighted={row['weighted_score']:.2f}, overall={row['overall_score']:.2f}, review_rate={row['review_rate']:.1f}%\n")
        f.write("\nProduct recommendation:\n")
        f.write("- Keep the safer balanced model as the default baseline.\n")
        f.write("- Add automatic review queues for high-risk questions and low risk-control answers.\n")
        f.write("- Improve concise answers by requiring concrete steps and uncertainty language.\n")

    print(f"{SUMMARY_PATH.relative_to(ROOT)} created.")


if __name__ == "__main__":
    main()
