from pathlib import Path
import itertools
import numpy as np
import pandas as pd
from utils_reports import md_table

ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data"
REPORTS_DIR = ROOT / "reports"
SOURCE_RATINGS = DATA_DIR / "ratings.csv"
MULTI_RATER_SAMPLE = DATA_DIR / "human_annotation_multi_rater_sample.csv"
COMPLETED = DATA_DIR / "human_annotation_multi_rater_completed.csv"
MERGED = DATA_DIR / "human_annotation_merged.csv"
OUT_CSV = REPORTS_DIR / "human_reliability_summary.csv"
OUT_BY_DIMENSION = REPORTS_DIR / "human_reliability_by_dimension.csv"
OUT_RATER_BIAS = REPORTS_DIR / "rater_bias_summary.csv"
OUT_MD = REPORTS_DIR / "human_reliability_report.md"

SCORE_COLS = ["accuracy", "helpfulness", "clarity", "actionability", "risk_control"]
ANNOTATION_SCORE_MAP = {
    "usefulness_score": "helpfulness",
    "specificity_score": "clarity",
    "actionability_score": "actionability",
    "empathy_score": "accuracy",
    "risk_control_score": "risk_control",
}


def clamp_score(x: float) -> float:
    return float(min(5, max(1, round(x * 2) / 2)))


def create_demo_multi_rater_sample() -> pd.DataFrame:
    """Create a realistic demo file so the workflow can run before real raters exist."""
    df = pd.read_csv(SOURCE_RATINGS).head(45).copy()
    if "answer_id" not in df.columns:
        df["answer_id"] = df["question_id"].astype(str) + "__" + df["model_name"].astype(str)
    rows = []
    rater_offsets = {
        "R1": {"accuracy": 0.0, "helpfulness": 0.0, "clarity": 0.0, "actionability": 0.0, "risk_control": 0.0},
        "R2": {"accuracy": -0.1, "helpfulness": 0.1, "clarity": 0.0, "actionability": -0.2, "risk_control": 0.1},
        "R3": {"accuracy": 0.1, "helpfulness": -0.1, "clarity": 0.1, "actionability": 0.0, "risk_control": -0.1},
    }
    for _, row in df.iterrows():
        for rater_id, offsets in rater_offsets.items():
            new = row.copy()
            new["rater_id"] = rater_id
            for col in SCORE_COLS:
                # deterministic pseudo-noise from answer id, dimension, and rater id
                seed_value = sum(ord(ch) for ch in f"{row['answer_id']}-{col}-{rater_id}")
                noise = ((seed_value % 5) - 2) * 0.1
                new[col] = clamp_score(float(row[col]) + offsets[col] + noise)
            new["overall_score"] = round(float(np.mean([new[col] for col in SCORE_COLS])), 2)
            rows.append(new)
    sample = pd.DataFrame(rows)
    sample.to_csv(MULTI_RATER_SAMPLE, index=False)
    return sample


def icc_oneway_random(df: pd.DataFrame, score_col: str) -> float:
    """Approximate ICC(1,1) for balanced or near-balanced rater data."""
    pivot = df.pivot_table(index="answer_id", columns="rater_id", values=score_col, aggfunc="mean").dropna()
    if pivot.shape[0] < 2 or pivot.shape[1] < 2:
        return np.nan
    values = pivot.to_numpy(dtype=float)
    n, k = values.shape
    grand_mean = values.mean()
    mean_targets = values.mean(axis=1)
    ss_between = k * ((mean_targets - grand_mean) ** 2).sum()
    ss_within = ((values - mean_targets[:, None]) ** 2).sum()
    ms_between = ss_between / (n - 1)
    ms_within = ss_within / (n * (k - 1))
    denom = ms_between + (k - 1) * ms_within
    return float((ms_between - ms_within) / denom) if denom else np.nan


def pairwise_agreement(df: pd.DataFrame, score_col: str) -> dict:
    pivot = df.pivot_table(index="answer_id", columns="rater_id", values=score_col, aggfunc="mean").dropna()
    if pivot.shape[1] < 2:
        return {"mean_abs_disagreement": np.nan, "within_0_5_rate": np.nan, "within_1_0_rate": np.nan}
    diffs = []
    for a, b in itertools.combinations(pivot.columns, 2):
        diffs.extend((pivot[a] - pivot[b]).abs().tolist())
    diffs = np.array(diffs, dtype=float)
    return {
        "mean_abs_disagreement": round(float(diffs.mean()), 3),
        "median_abs_disagreement": round(float(np.median(diffs)), 3),
        "within_0_5_rate": round(float((diffs <= 0.5).mean() * 100), 1),
        "within_1_0_rate": round(float((diffs <= 1.0).mean() * 100), 1),
    }


def krippendorff_alpha_interval_approx(df: pd.DataFrame, score_col: str) -> float:
    pivot = df.pivot_table(index="answer_id", columns="rater_id", values=score_col, aggfunc="mean")
    values = pivot.to_numpy(dtype=float)
    observed = []
    for row in values:
        row = row[~np.isnan(row)]
        observed.extend((a - b) ** 2 for a, b in itertools.combinations(row, 2))
    all_values = df[score_col].dropna().to_numpy(dtype=float)
    expected = [(a - b) ** 2 for a, b in itertools.combinations(all_values, 2)]
    if not observed or not expected or np.mean(expected) == 0:
        return np.nan
    return float(1 - (np.mean(observed) / np.mean(expected)))


def normalize_annotation_scores(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    for source, target in ANNOTATION_SCORE_MAP.items():
        if source in out.columns and target not in out.columns:
            out[target] = out[source]
    if "risk_level" in out.columns and "expected_risk" not in out.columns:
        out["expected_risk"] = out["risk_level"]
    if "student_question" in out.columns and "question_text" not in out.columns:
        out["question_text"] = out["student_question"]
    if "answer_id" not in out.columns and {"question_id", "model_name"}.issubset(out.columns):
        out["answer_id"] = out["question_id"].astype(str) + "__" + out["model_name"].astype(str)
    return out


def main() -> None:
    REPORTS_DIR.mkdir(exist_ok=True)
    source = MERGED if MERGED.exists() else (COMPLETED if COMPLETED.exists() else MULTI_RATER_SAMPLE)
    if not source.exists():
        df = create_demo_multi_rater_sample()
        source = MULTI_RATER_SAMPLE
    else:
        df = pd.read_csv(source)
    df = normalize_annotation_scores(df)

    for col in SCORE_COLS:
        df[col] = pd.to_numeric(df[col], errors="coerce")
    if "answer_id" not in df.columns:
        df["answer_id"] = df["question_id"].astype(str) + "__" + df["model_name"].astype(str)
    df = df.dropna(subset=["answer_id", "rater_id"] + SCORE_COLS).copy()
    if "overall_score" not in df.columns or df["overall_score"].isna().all():
        df["overall_score"] = df[SCORE_COLS].mean(axis=1).round(2)

    dimensions = SCORE_COLS + ["overall_score"]
    rows = []
    for col in dimensions:
        pairwise = pairwise_agreement(df, col)
        rows.append({
            "dimension": col,
            "icc_1_1": round(icc_oneway_random(df, col), 3),
            "krippendorff_alpha_approx": round(krippendorff_alpha_interval_approx(df, col), 3),
            **pairwise,
        })
    summary = pd.DataFrame(rows)
    summary.to_csv(OUT_CSV, index=False)
    summary.to_csv(OUT_BY_DIMENSION, index=False)

    long = df.melt(id_vars=["answer_id", "rater_id"], value_vars=dimensions, var_name="dimension", value_name="score").dropna()
    item_means = long.groupby(["answer_id", "dimension"])["score"].mean().rename("item_mean").reset_index()
    bias = long.merge(item_means, on=["answer_id", "dimension"], how="left")
    bias["score_minus_item_mean"] = bias["score"] - bias["item_mean"]
    rater_bias = bias.groupby(["rater_id", "dimension"]).agg(
        mean_score=("score", "mean"),
        mean_offset_vs_item_mean=("score_minus_item_mean", "mean"),
        rated_answers=("answer_id", "nunique"),
    ).reset_index()
    rater_bias[["mean_score", "mean_offset_vs_item_mean"]] = rater_bias[["mean_score", "mean_offset_vs_item_mean"]].round(3)
    rater_bias.to_csv(OUT_RATER_BIAS, index=False)

    answer_count = df["answer_id"].nunique()
    rater_count = df["rater_id"].nunique()
    overall_icc = summary.loc[summary["dimension"] == "overall_score", "icc_1_1"].iloc[0]
    weakest = summary.sort_values(["within_1_0_rate", "icc_1_1"], ascending=[True, True]).iloc[0]
    strongest = summary.sort_values(["within_1_0_rate", "icc_1_1"], ascending=[False, False]).iloc[0]

    interpretation = "usable for demo"
    if pd.notna(overall_icc) and overall_icc >= 0.75:
        interpretation = "strong agreement"
    elif pd.notna(overall_icc) and overall_icc >= 0.5:
        interpretation = "moderate agreement; refine rubric before strong claims"
    else:
        interpretation = "weak agreement; use for workflow demo only"

    lines = [
        "# Human Reliability Report",
        "",
        f"Source file: `{source.relative_to(ROOT)}`",
        f"Unique answers scored: **{answer_count}**",
        f"Unique raters: **{rater_count}**",
        "",
        "## Reliability Summary",
        "",
        md_table(summary),
        "",
        "## Rater Severity / Leniency",
        "",
        md_table(rater_bias, max_rows=80),
        "",
        "## Interpretation",
        "",
        f"Overall-score reliability is **{overall_icc}**, which is best treated as **{interpretation}**.",
        f"The most reliable dimension in this run is **{strongest['dimension']}** by within-one-point agreement.",
        f"The most subjective dimension is **{weakest['dimension']}**; this is the first place to tighten rubric examples and rater training.",
        "Percent agreement within ±1 point is usually easier to interpret than a single reliability coefficient for early rubric pilots.",
        "The Krippendorff-style alpha value here is an approximation for interval-style scores and should be treated as a directional diagnostic, not a formal publication-grade estimate.",
        "",
        "## Product Meaning",
        "",
        "This report prevents the project from pretending that human scores are automatically objective. A mature HCAI evaluation system must measure rater disagreement, not hide it.",
        "",
        "## Next Step",
        "",
        "Replace the demo sample with `data/human_annotation_multi_rater_completed.csv` after 2–3 real raters score the same answer set.",
    ]
    OUT_MD.write_text("\n".join(lines), encoding="utf-8")
    print(f"Created {OUT_CSV.relative_to(ROOT)}")
    print(f"Created {OUT_BY_DIMENSION.relative_to(ROOT)}")
    print(f"Created {OUT_RATER_BIAS.relative_to(ROOT)}")
    print(f"Created {OUT_MD.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
