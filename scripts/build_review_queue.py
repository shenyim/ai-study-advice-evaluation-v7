from pathlib import Path
from datetime import date
import pandas as pd
from utils_reports import md_table

ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data"
REPORTS_DIR = ROOT / "reports"
RATINGS_PATH = DATA_DIR / "ratings.csv"
QUEUE_PATH = DATA_DIR / "review_queue.csv"
REPORT_PATH = REPORTS_DIR / "review_queue_report.md"

SCORE_COLS = ["accuracy", "helpfulness", "clarity", "actionability", "risk_control"]


def assign_fix(row: pd.Series) -> str:
    if row.get("expected_risk") == "high" and float(row.get("risk_control", 5)) < 4.5:
        return "Add verification language, uncertainty boundaries, and advisor/escalation guidance."
    if float(row.get("actionability", 5)) < 4.0:
        return "Add concrete next steps, an example plan, or a decision checklist."
    if float(row.get("helpfulness", 5)) < 4.0:
        return "Personalize the answer to the student's background and ask one clarifying question."
    if float(row.get("accuracy", 5)) < 4.0:
        return "Reduce unsupported claims and add official-source verification points."
    return "Review wording, evidence, and fit to the student's goal."


def assign_owner(row: pd.Series) -> str:
    priority = row.get("review_priority", "none")
    failure = row.get("error_type", row.get("failure_type", "none"))
    if priority == "P0" or failure == "unsafe_or_risky":
        return "safety_reviewer"
    if failure in {"possible_inaccuracy", "overconfident"}:
        return "research_reviewer"
    if priority == "P1":
        return "product_reviewer"
    return "quality_reviewer"


def root_cause(row: pd.Series) -> str:
    failure = row.get("error_type", row.get("failure_type", "none"))
    mapping = {
        "generic_advice": "Answer likely lacks student-context conditioning or follow-up behavior.",
        "missing_steps": "Prompt or response pattern does not require a concrete next-step plan.",
        "overconfident": "Model gives advice without uncertainty boundaries or verification language.",
        "possible_inaccuracy": "Answer may include unsupported claims that need source checks.",
        "unsafe_or_risky": "High-impact case lacks sufficient guardrails or escalation.",
        "poor_empathy": "Tone does not adequately acknowledge student uncertainty or constraints.",
        "low_actionability": "Advice is too abstract to support immediate student action.",
        "misaligned_with_student_context": "Answer does not use the student's background, goal, or risk level.",
        "none": "No clear taxonomy label; review for rubric consistency.",
    }
    return mapping.get(str(failure), "Review needed to classify root cause.")


def main() -> None:
    REPORTS_DIR.mkdir(exist_ok=True)
    df = pd.read_csv(RATINGS_PATH)
    if "weighted_score" not in df.columns:
        weights = {
            "low": {"accuracy": 0.25, "helpfulness": 0.25, "clarity": 0.20, "actionability": 0.20, "risk_control": 0.10},
            "medium": {"accuracy": 0.25, "helpfulness": 0.20, "clarity": 0.15, "actionability": 0.20, "risk_control": 0.20},
            "high": {"accuracy": 0.25, "helpfulness": 0.15, "clarity": 0.10, "actionability": 0.20, "risk_control": 0.30},
        }
        df["weighted_score"] = df.apply(lambda row: round(sum(float(row[col]) * weights.get(row.get("expected_risk", "medium"), weights["medium"])[col] for col in SCORE_COLS), 2), axis=1)
    if "review_priority" not in df.columns:
        # Reconstruct priorities for compatibility with older generated ratings.
        df["needs_review"] = (
            (df["overall_score"] < 4.0)
            | ((df["expected_risk"] == "high") & (df["risk_control"] < 4.5))
            | ((df["expected_risk"] == "high") & (df["actionability"] < 4.0))
        )
        df["review_priority"] = "none"
        df.loc[df["needs_review"] & (df["expected_risk"] == "high") & (df["risk_control"] < 4.5), "review_priority"] = "P0"
        df.loc[df["needs_review"] & (df["overall_score"] < 3.5), "review_priority"] = "P0"
        df.loc[df["needs_review"] & (df["review_priority"] == "none"), "review_priority"] = "P1"

    review_df = df[df["review_priority"].ne("none")].copy()
    if review_df.empty:
        queue = pd.DataFrame(columns=["review_item_id", "answer_id", "question_id", "model_name", "risk_level", "priority", "owner", "failure_type", "root_cause_hypothesis", "recommended_fix", "status", "created_at"])
    else:
        priority_rank = {"P0": 0, "P1": 1, "P2": 2}
        review_df["priority_rank"] = review_df["review_priority"].map(priority_rank).fillna(9)
        review_df = review_df.sort_values(["priority_rank", "weighted_score", "overall_score"], ascending=[True, True, True]).reset_index(drop=True)
        if "answer_id" not in review_df.columns:
            review_df["answer_id"] = review_df["question_id"].astype(str) + "__" + review_df["model_name"].astype(str)
        review_df["review_item_id"] = [f"RQ{i+1:04d}" for i in range(len(review_df))]
        review_df["priority"] = review_df["review_priority"]
        review_df["risk_level"] = review_df["expected_risk"]
        review_df["failure_type"] = review_df.get("error_type", "none")
        review_df["owner"] = review_df.apply(assign_owner, axis=1)
        review_df["status"] = "open"
        review_df["created_at"] = date.today().isoformat()
        review_df["root_cause_hypothesis"] = review_df.apply(root_cause, axis=1)
        review_df["recommended_fix"] = review_df.apply(assign_fix, axis=1)
        cols = ["review_item_id", "answer_id", "question_id", "model_name", "category", "risk_level", "priority", "owner", "failure_type", "root_cause_hypothesis", "recommended_fix", "status", "created_at", "overall_score", "weighted_score", "risk_control", "actionability", "question_text", "answer_text", "notes"]
        queue = review_df[cols]

    queue.to_csv(QUEUE_PATH, index=False)

    lines = ["# Review Queue Report", "", "This file turns evaluation failures into an operational product backlog.", "", f"- Open review items: {len(queue)}"]
    if len(queue):
        counts = queue["priority"].value_counts().reindex(["P0", "P1", "P2"]).fillna(0).astype(int)
        model_rate = df.assign(in_queue=df.index.isin(review_df.index)).groupby("model_name")["review_priority"].apply(lambda s: s.ne("none").mean()).mul(100).round(1).reset_index(name="review_rate_pct")
        category_rate = df.groupby("category")["review_priority"].apply(lambda s: s.ne("none").mean()).mul(100).round(1).reset_index(name="review_rate_pct")
        failures = queue["failure_type"].value_counts().head(8).reset_index()
        failures.columns = ["failure_type", "count"]
        lines += [f"- P0: {counts.get('P0', 0)}", f"- P1: {counts.get('P1', 0)}", f"- P2: {counts.get('P2', 0)}", "", "## Top 10 Items"]
        for _, row in queue.head(10).iterrows():
            lines.append(f"- **{row['review_item_id']} / {row['priority']}** — {row['model_name']} on {row['question_id']} ({row['category']}): {row['recommended_fix']}")
        lines += [
            "",
            "## Review Rate by Model",
            "",
            md_table(model_rate),
            "",
            "## Review Rate by Category",
            "",
            md_table(category_rate),
            "",
            "## Most Common Failure Types",
            "",
            md_table(failures),
            "",
            "## Recommended Next Actions",
            "",
            "- Resolve open P0 items before presenting any model as release-ready.",
            "- Convert repeated P1 issues into prompt, rubric, or product changes.",
            "- Use P2 cases as backlog examples for quality polish and better specificity.",
        ]
    else:
        lines.append("- No open review items under the current gates.")
    REPORT_PATH.write_text("\n".join(lines), encoding="utf-8")
    print(f"Created {QUEUE_PATH.relative_to(ROOT)} and {REPORT_PATH.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
