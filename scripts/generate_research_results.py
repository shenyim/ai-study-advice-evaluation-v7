from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
REPORTS_DIR = ROOT / "reports"
DATA_DIR = ROOT / "data"
OUT_MD = REPORTS_DIR / "research_results_discussion.md"


def read_text(path: Path, fallback: str = "Not generated yet.") -> str:
    return path.read_text(encoding="utf-8") if path.exists() else fallback


def main() -> None:
    REPORTS_DIR.mkdir(exist_ok=True)
    ratings = pd.read_csv(DATA_DIR / "ratings.csv")
    model_summary_path = REPORTS_DIR / "model_comparison_summary.csv"
    model_summary = pd.read_csv(model_summary_path) if model_summary_path.exists() else pd.DataFrame()
    best_model = "unknown"
    weakest_dimension = "unknown"
    if not model_summary.empty and "weighted_score" in model_summary.columns:
        best_model = model_summary.sort_values("weighted_score", ascending=False).iloc[0]["model_name"]
    score_cols = ["accuracy", "helpfulness", "clarity", "actionability", "risk_control"]
    weakest_dimension = ratings[score_cols].mean().sort_values().index[0]
    review_rate = ratings["needs_review"].mean() * 100 if "needs_review" in ratings.columns else 0
    p0_rate = (ratings["review_priority"].eq("P0").mean() * 100) if "review_priority" in ratings.columns else 0

    lines = [
        "# Research Results and Discussion",
        "",
        "## Research Question",
        "",
        "How can a human-centered evaluation workflow compare AI-generated student advice across usefulness, actionability, and risk control?",
        "",
        "## Method Summary",
        "",
        "The system evaluates student-advice answers using a five-dimension rubric: accuracy, helpfulness, clarity, actionability, and risk control. Scores are converted into risk-weighted product metrics and review priorities.",
        "",
        "## Key Findings",
        "",
        f"- The strongest current model candidate is **{best_model}** under the risk-weighted scoring setup.",
        f"- The weakest evaluation dimension is **{weakest_dimension}**, which should drive the next prompt/product iteration.",
        f"- The current review rate is **{review_rate:.1f}%**, meaning the system still finds a meaningful number of cases requiring human review.",
        f"- The P0 rate is **{p0_rate:.1f}%**, which is the main launch-readiness blocker for a real student-facing system.",
        "",
        "## HCAI Interpretation",
        "",
        "The central product lesson is that advice quality cannot be reduced to whether an answer sounds fluent. In student-advice settings, the most important failures are often subtle: overconfidence, missing caveats, vague next steps, or weak escalation guidance for high-impact decisions.",
        "",
        "## Limitations",
        "",
        "- The current default dataset uses simulated model outputs.",
        "- Human annotation examples are included as workflow scaffolding, not final evidence.",
        "- The rubric needs real rater calibration before making strong empirical claims.",
        "- Student privacy, consent, and institutional deployment constraints are outside the demo scope.",
        "",
        "## Next Iteration",
        "",
        "1. Replace simulated model outputs with real outputs from multiple LLMs.",
        "2. Recruit 2–3 raters and compute inter-rater reliability.",
        "3. Run pairwise model comparison using human-scored results.",
        "4. Convert top failure modes into prompt rules, UI warnings, and review policies.",
    ]
    OUT_MD.write_text("\n".join(lines), encoding="utf-8")
    print(f"Created {OUT_MD.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
