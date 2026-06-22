import pandas as pd

from utils_io import load_evaluation_config
from utils_paths import DATA_DIR, REPORTS_DIR, ensure_project_dirs, rel
from utils_reports import md_table, write_markdown


OUT_PATH = REPORTS_DIR / "final_research_report.md"


def safe_read(path):
    return pd.read_csv(path) if path.exists() else pd.DataFrame()


def main() -> None:
    ensure_project_dirs()
    config = load_evaluation_config()
    ratings = safe_read(DATA_DIR / "ratings.csv")
    leaderboard = safe_read(REPORTS_DIR / "model_leaderboard.csv")
    reliability = safe_read(REPORTS_DIR / "human_reliability_summary.csv")
    pairwise = safe_read(REPORTS_DIR / "model_pairwise_differences.csv")
    queue = safe_read(DATA_DIR / "review_queue.csv")

    questions = ratings["question_id"].nunique() if "question_id" in ratings else 0
    answers = len(ratings)
    models = ratings["model_name"].nunique() if "model_name" in ratings else 0
    avg = ratings["overall_score"].mean() if "overall_score" in ratings else float("nan")
    review_rate = ratings["needs_review"].mean() if "needs_review" in ratings else float("nan")

    lines = [
        "# AI Study Advice Evaluation Platform",
        "",
        "## Abstract",
        "",
        "This project is a human-centered AI evaluation platform for student-advice systems. It supports simulated and real model outputs, risk-aware scoring, human annotation, reliability analysis, bootstrap model comparison, launch readiness checks, and a Streamlit dashboard.",
        "",
        "## Introduction",
        "",
        "Student-facing AI advice can sound polished while still being vague, overconfident, or unsafe for academic and career decisions. This project evaluates advice quality as a human-centered product and research problem.",
        "",
        "## Research Question",
        "",
        "How can AI-generated student advice be evaluated across quality, actionability, empathy, and risk control while producing evidence useful for model selection and product iteration?",
        "",
        "## System Overview",
        "",
        f"Active evaluation mode: **{config.get('mode', 'simulated')}**.",
        "The pipeline creates or imports model answers, scores them, builds a review backlog, analyzes human reliability, compares models statistically, and generates research and portfolio outputs.",
        "",
        "## Dataset",
        "",
        f"- Unique questions: **{questions}**",
        f"- Evaluated answers: **{answers}**",
        f"- Model candidates: **{models}**",
        "",
        "## Evaluation Rubric",
        "",
        "The scoring layer uses accuracy, helpfulness, clarity, actionability, and risk control. Human annotation maps usefulness, specificity, actionability, empathy, and risk control into the same analysis layer for compatibility.",
        "",
        "## Human Annotation Workflow",
        "",
        "The workflow includes annotation templates, rater batches, merge logic, completeness checks, rater coverage, and reliability diagnostics.",
        "",
        "## Model Comparison Method",
        "",
        "Models are compared with average overall score, risk-weighted score, review rate, P0/P1/P2 pressure, high-risk performance, failure taxonomy, and bootstrap confidence intervals.",
        "",
        "## Results",
        "",
        f"- Average overall score: **{avg:.2f}**" if pd.notna(avg) else "- Average overall score: unavailable",
        f"- Review rate: **{review_rate:.1%}**" if pd.notna(review_rate) else "- Review rate: unavailable",
        "",
        md_table(leaderboard.head(10)) if not leaderboard.empty else "_Leaderboard unavailable._",
        "",
        "## Human Reliability Findings",
        "",
        md_table(reliability) if not reliability.empty else "_Reliability results unavailable or demo-only._",
        "",
        "## Statistical Evidence",
        "",
        md_table(pairwise) if not pairwise.empty else "_Pairwise bootstrap results unavailable._",
        "",
        "## Product Implications",
        "",
        f"The current review backlog contains **{len(queue)}** open items." if not queue.empty else "No open review queue items were generated under the current gates.",
        "The backlog links failure modes to owners, root-cause hypotheses, and recommended fixes.",
        "",
        "## Launch Readiness",
        "",
        "Launch readiness is assessed through configured gates, but passing demo gates does not imply real deployment readiness.",
        "",
        "## Limitations",
        "",
        "This is a portfolio and research demo, not a deployed student-advice product. Results depend on sample size, prompt setup, model version, rubric design, rater reliability, and dataset representativeness.",
        "",
        "## Future Work",
        "",
        "Expand real model collection, recruit independent raters, improve rubric examples, evaluate prompt interventions, add privacy controls, and test whether students understand and trust risk-aware advice appropriately.",
        "",
        "## Portfolio Summary",
        "",
        "The project demonstrates applied AI evaluation, human-centered data science, product analytics, research operations, statistical evidence, and responsible AI judgment.",
    ]
    write_markdown(OUT_PATH, lines)
    print(f"Wrote {rel(OUT_PATH)}")


if __name__ == "__main__":
    main()

