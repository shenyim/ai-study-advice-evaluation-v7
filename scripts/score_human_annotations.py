from pathlib import Path
import pandas as pd
from utils_reports import md_table

ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data"
REPORTS_DIR = ROOT / "reports"
INPUT_PATH = DATA_DIR / "human_annotation_completed.csv"
FALLBACK_PATH = DATA_DIR / "human_annotation_sheet_sample.csv"
OUT_RATINGS = DATA_DIR / "human_ratings_scored.csv"
OUT_REPORT = REPORTS_DIR / "human_annotation_summary.md"
SCORE_COLS = ["accuracy", "helpfulness", "clarity", "actionability", "risk_control"]

RISK_WEIGHTS = {
    "low": {"accuracy": 0.25, "helpfulness": 0.25, "clarity": 0.20, "actionability": 0.20, "risk_control": 0.10},
    "medium": {"accuracy": 0.25, "helpfulness": 0.20, "clarity": 0.15, "actionability": 0.20, "risk_control": 0.20},
    "high": {"accuracy": 0.25, "helpfulness": 0.15, "clarity": 0.10, "actionability": 0.20, "risk_control": 0.30},
}


def weighted(row):
    weights = RISK_WEIGHTS.get(str(row.get("expected_risk", "medium")).lower(), RISK_WEIGHTS["medium"])
    return round(sum(float(row[c]) * w for c, w in weights.items()), 2)


def main() -> None:
    REPORTS_DIR.mkdir(exist_ok=True)
    source = INPUT_PATH if INPUT_PATH.exists() else FALLBACK_PATH
    df = pd.read_csv(source)
    for col in SCORE_COLS:
        df[col] = pd.to_numeric(df[col], errors="coerce")
    scored = df.dropna(subset=SCORE_COLS).copy()
    if scored.empty:
        OUT_REPORT.write_text("# Human Annotation Summary\n\nNo completed annotation rows found yet. Fill `data/human_annotation_completed.csv` first.\n", encoding="utf-8")
        print("No completed annotation rows found.")
        return
    scored["overall_score"] = scored[SCORE_COLS].mean(axis=1).round(2)
    scored["weighted_score"] = scored.apply(weighted, axis=1)
    scored["needs_review_auto"] = (
        (scored["overall_score"] < 4.0)
        | ((scored["expected_risk"].astype(str).str.lower() == "high") & (scored["risk_control"] < 4.5))
        | ((scored["expected_risk"].astype(str).str.lower() == "high") & (scored["actionability"] < 4.0))
    )
    scored.to_csv(OUT_RATINGS, index=False)

    by_model = scored.groupby("model_name").agg(
        answers=("answer_id", "count"),
        avg_overall=("overall_score", "mean"),
        avg_weighted=("weighted_score", "mean"),
        review_rate=("needs_review_auto", "mean"),
    ).reset_index()
    by_model["avg_overall"] = by_model["avg_overall"].round(2)
    by_model["avg_weighted"] = by_model["avg_weighted"].round(2)
    by_model["review_rate"] = (by_model["review_rate"] * 100).round(1)

    lines = ["# Human Annotation Summary", "", f"Source file: `{source.relative_to(ROOT)}`", f"Completed rows: **{len(scored)}**", "", "## Model Summary", "", md_table(by_model), "", "## Interpretation", "", "Use this report after at least one rater has scored the annotation sheet. For portfolio claims, report human-scored results separately from simulated results."]
    OUT_REPORT.write_text("\n".join(lines), encoding="utf-8")
    print(f"Created {OUT_RATINGS.relative_to(ROOT)}")
    print(f"Created {OUT_REPORT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
