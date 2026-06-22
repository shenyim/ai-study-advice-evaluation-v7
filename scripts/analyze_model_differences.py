from pathlib import Path
import itertools
import numpy as np
import pandas as pd
from utils_reports import md_table

try:
    import matplotlib.pyplot as plt
except ModuleNotFoundError:
    plt = None

ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data"
REPORTS_DIR = ROOT / "reports"
RATINGS_PATH = DATA_DIR / "ratings.csv"
OUT_CSV = REPORTS_DIR / "model_pairwise_differences.csv"
OUT_CATEGORY_CSV = REPORTS_DIR / "model_category_differences.csv"
OUT_HIGH_RISK_CSV = REPORTS_DIR / "high_risk_model_differences.csv"
OUT_FIGURE = ROOT / "figures" / "bootstrap_confidence_intervals.png"
OUT_MD = REPORTS_DIR / "statistical_analysis.md"

METRIC = "weighted_score"
BOOTSTRAP_N = 800
RANDOM_SEED = 42


def bootstrap_diff(a: pd.Series, b: pd.Series, n: int = BOOTSTRAP_N) -> tuple[float, float, float]:
    rng = np.random.default_rng(RANDOM_SEED)
    a_vals = a.dropna().to_numpy(dtype=float)
    b_vals = b.dropna().to_numpy(dtype=float)
    if len(a_vals) == 0 or len(b_vals) == 0:
        return np.nan, np.nan, np.nan
    diffs = []
    for _ in range(n):
        sample_a = rng.choice(a_vals, size=len(a_vals), replace=True)
        sample_b = rng.choice(b_vals, size=len(b_vals), replace=True)
        diffs.append(sample_a.mean() - sample_b.mean())
    return float(np.mean(diffs)), float(np.percentile(diffs, 2.5)), float(np.percentile(diffs, 97.5))


def cohens_d(a: pd.Series, b: pd.Series) -> float:
    a_vals = a.dropna().to_numpy(dtype=float)
    b_vals = b.dropna().to_numpy(dtype=float)
    if len(a_vals) < 2 or len(b_vals) < 2:
        return np.nan
    pooled = np.sqrt(((len(a_vals) - 1) * a_vals.var(ddof=1) + (len(b_vals) - 1) * b_vals.var(ddof=1)) / (len(a_vals) + len(b_vals) - 2))
    return float((a_vals.mean() - b_vals.mean()) / pooled) if pooled else np.nan


def evidence_label(low: float, high: float, diff: float) -> str:
    if pd.isna(low) or pd.isna(high):
        return "insufficient"
    if low > 0 or high < 0:
        return "strong" if abs(diff) >= 0.3 else "moderate"
    if abs(diff) >= 0.3:
        return "weak but directionally meaningful"
    return "weak"


def pairwise_table(df: pd.DataFrame, group_cols: list[str] | None = None) -> pd.DataFrame:
    rows = []
    group_cols = group_cols or []
    grouped = [((), df)] if not group_cols else df.groupby(group_cols)
    for keys, group in grouped:
        if not isinstance(keys, tuple):
            keys = (keys,)
        models = sorted(group["model_name"].dropna().unique())
        for model_a, model_b in itertools.combinations(models, 2):
            a = group.loc[group["model_name"] == model_a, METRIC]
            b = group.loc[group["model_name"] == model_b, METRIC]
            diff, low, high = bootstrap_diff(a, b)
            record = {col: value for col, value in zip(group_cols, keys)}
            record.update({
                "metric": METRIC,
                "model_a": model_a,
                "model_b": model_b,
                "mean_a": round(float(a.mean()), 3),
                "mean_b": round(float(b.mean()), 3),
                "mean_diff_a_minus_b": round(diff, 3),
                "bootstrap_ci_2_5": round(low, 3),
                "bootstrap_ci_97_5": round(high, 3),
                "effect_size_cohens_d": round(cohens_d(a, b), 3),
                "ci_crosses_zero": not bool(low > 0 or high < 0),
                "evidence_strength": evidence_label(low, high, diff),
            })
            rows.append(record)
    return pd.DataFrame(rows)


def main() -> None:
    REPORTS_DIR.mkdir(exist_ok=True)
    OUT_FIGURE.parent.mkdir(exist_ok=True)
    df = pd.read_csv(RATINGS_PATH)
    if "answer_id" not in df.columns:
        df["answer_id"] = df["question_id"].astype(str) + "__" + df["model_name"].astype(str)
    if METRIC not in df.columns:
        raise ValueError(f"{METRIC} missing. Run analyze_ratings.py first.")
    out = pairwise_table(df).sort_values("mean_diff_a_minus_b", ascending=False)
    out.to_csv(OUT_CSV, index=False)
    category_out = pairwise_table(df, ["category"]).sort_values(["category", "mean_diff_a_minus_b"], ascending=[True, False])
    category_out.to_csv(OUT_CATEGORY_CSV, index=False)
    high_risk = df[df["expected_risk"].eq("high")].copy()
    high_risk_out = pairwise_table(high_risk).sort_values("mean_diff_a_minus_b", ascending=False) if not high_risk.empty else pd.DataFrame()
    high_risk_out.to_csv(OUT_HIGH_RISK_CSV, index=False)

    if not out.empty and plt is not None:
        labels = out["model_a"] + " - " + out["model_b"]
        y = np.arange(len(out))
        fig, ax = plt.subplots(figsize=(9, max(4, len(out) * 0.45)))
        ax.errorbar(out["mean_diff_a_minus_b"], y, xerr=[out["mean_diff_a_minus_b"] - out["bootstrap_ci_2_5"], out["bootstrap_ci_97_5"] - out["mean_diff_a_minus_b"]], fmt="o")
        ax.axvline(0, color="black", linewidth=1)
        ax.set_yticks(y)
        ax.set_yticklabels(labels)
        ax.set_xlabel("Bootstrap mean difference in risk-weighted score")
        ax.set_title("Pairwise Model Difference Confidence Intervals")
        fig.tight_layout()
        fig.savefig(OUT_FIGURE)
        plt.close(fig)
    elif plt is None:
        print(f"WARNING: matplotlib unavailable; skipped {OUT_FIGURE.name}")

    leaderboard = df.groupby("model_name").agg(
        answers=("answer_id", "count"),
        avg_weighted=(METRIC, "mean"),
        avg_overall=("overall_score", "mean"),
        review_rate=("needs_review", "mean"),
    ).reset_index()
    leaderboard["avg_weighted"] = leaderboard["avg_weighted"].round(3)
    leaderboard["avg_overall"] = leaderboard["avg_overall"].round(3)
    leaderboard["review_rate"] = (leaderboard["review_rate"] * 100).round(1)
    leaderboard = leaderboard.sort_values("avg_weighted", ascending=False)

    best = leaderboard.iloc[0]["model_name"] if len(leaderboard) else "unknown"
    lines = [
        "# Statistical Analysis",
        "",
        "This is a lightweight statistical layer for a portfolio/research prototype. It uses bootstrap confidence intervals instead of claiming formal production-grade inference.",
        "",
        "## Model Leaderboard",
        "",
        md_table(leaderboard),
        "",
        "## Pairwise Differences",
        "",
        md_table(out),
        "",
        "## Category-Level Differences",
        "",
        md_table(category_out, max_rows=40) if not category_out.empty else "_No category-level comparisons available._",
        "",
        "## High-Risk-Only Differences",
        "",
        md_table(high_risk_out) if not high_risk_out.empty else "_No high-risk comparisons available._",
        "",
        "## Interpretation",
        "",
        f"The current best release-candidate model by risk-weighted score is **{best}**.",
        "A difference is directionally meaningful when the average gap is non-trivial and the confidence interval mostly supports the same direction.",
        "If a bootstrap confidence interval crosses zero, evidence is weak or mixed for that pair under the current sample.",
        "Evidence labels are weak, moderate, or strong diagnostics for this dataset; they are not formal large-scale benchmark claims.",
        "This is not a formal large-scale benchmark unless the dataset is expanded with real model outputs, fixed prompts, and reliable human scoring.",
    ]
    OUT_MD.write_text("\n".join(lines), encoding="utf-8")
    print(f"Created {OUT_CSV.relative_to(ROOT)}")
    print(f"Created {OUT_MD.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
