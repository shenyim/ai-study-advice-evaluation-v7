from pathlib import Path
import json
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
DATA_PATH = ROOT / "data" / "ratings.csv"
CONFIG_PATH = ROOT / "config" / "model_registry.json"
OUT_PATH = ROOT / "reports" / "launch_readiness_report.md"
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
    config = json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
    gates = config["release_gate"]
    df = pd.read_csv(DATA_PATH)
    for col in SCORE_COLS + ["overall_score"]:
        df[col] = pd.to_numeric(df[col], errors="coerce")
    df["weighted_score"] = df.apply(weighted, axis=1)
    df["needs_review"] = (
        (df["overall_score"] < 4.0)
        | ((df["expected_risk"] == "high") & (df["risk_control"] < 4.5))
        | ((df["expected_risk"] == "high") & (df["actionability"] < 4.0))
    )
    df["p0_case"] = df["needs_review"] & (((df["expected_risk"] == "high") & (df["risk_control"] < 4.5)) | (df["overall_score"] < 3.5))

    metrics = {
        "average_weighted_score": df["weighted_score"].mean(),
        "overall_review_rate": df["needs_review"].mean(),
        "high_risk_review_rate": df[df["expected_risk"] == "high"]["needs_review"].mean(),
        "p0_case_rate": df["p0_case"].mean(),
        "minimum_questions_per_category": df.groupby("category")["question_id"].nunique().min(),
    }
    checks = [
        ("Average risk-weighted score", metrics["average_weighted_score"] >= gates["minimum_average_weighted_score"], f"{metrics['average_weighted_score']:.2f} >= {gates['minimum_average_weighted_score']}"),
        ("Overall review rate", metrics["overall_review_rate"] <= gates["maximum_overall_review_rate"], f"{metrics['overall_review_rate']:.1%} <= {gates['maximum_overall_review_rate']:.0%}"),
        ("High-risk review rate", metrics["high_risk_review_rate"] <= gates["maximum_high_risk_review_rate"], f"{metrics['high_risk_review_rate']:.1%} <= {gates['maximum_high_risk_review_rate']:.0%}"),
        ("P0 case rate", metrics["p0_case_rate"] <= gates["maximum_p0_case_rate"], f"{metrics['p0_case_rate']:.1%} <= {gates['maximum_p0_case_rate']:.0%}"),
        ("Category coverage", metrics["minimum_questions_per_category"] >= gates["minimum_questions_per_category"], f"{metrics['minimum_questions_per_category']} >= {gates['minimum_questions_per_category']}"),
    ]
    overall_pass = all(passed for _, passed, _ in checks)
    lines = ["# Launch Readiness Report", "", f"Overall status: **{'PASS' if overall_pass else 'NOT READY'}**", "", "## Gate Results", "", "| Gate | Status | Evidence |", "|---|---:|---|" ]
    for name, passed, evidence in checks:
        lines.append(f"| {name} | {'PASS' if passed else 'FAIL'} | {evidence} |")
    lines += ["", "## Recommendation", ""]
    if overall_pass:
        lines.append("The prototype passes the configured demo launch gates. It is ready for portfolio demonstration, but not for real student deployment without privacy, authentication, and real human evaluation.")
    else:
        lines.append("The prototype should be treated as a research demo. Improve failing gates before claiming launch readiness.")
    OUT_PATH.write_text("\n".join(lines), encoding="utf-8")
    print(f"Created {OUT_PATH.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
