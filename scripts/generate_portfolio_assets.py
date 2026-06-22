from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
REPORTS_DIR = ROOT / "reports"
DOCS_DIR = ROOT / "docs"
RATINGS_PATH = ROOT / "data" / "ratings.csv"
LEADERBOARD_PATH = REPORTS_DIR / "model_leaderboard.csv"
ONE_PAGER = REPORTS_DIR / "project_one_pager.md"
HTML_PATH = DOCS_DIR / "index.html"


def main() -> None:
    REPORTS_DIR.mkdir(exist_ok=True)
    DOCS_DIR.mkdir(exist_ok=True)
    df = pd.read_csv(RATINGS_PATH)
    leaderboard = pd.read_csv(LEADERBOARD_PATH) if LEADERBOARD_PATH.exists() else pd.DataFrame()
    best = leaderboard.iloc[0]["model_name"] if not leaderboard.empty else "Balanced_GPT"
    questions = df["question_id"].nunique()
    answers = len(df)
    models = df["model_name"].nunique()
    review_rate = df["needs_review"].mean() if "needs_review" in df.columns else (df["overall_score"] < 4).mean()

    one_pager = f"""# AI Study Advice Evaluation Platform — One Pager

## Problem
Student-facing AI advice can sound confident even when it is vague, risky, or not actionable. A normal chatbot demo does not show whether the advice is actually safe enough for academic, research, or career decisions.

## Solution
This project builds a human-centered AI evaluation layer for student-advice systems. It compares model candidates using a five-dimension rubric, risk-aware weighting, quality gates, failure taxonomy, and a human review queue.

## Current Demo Scope
- Student scenarios: **{questions}**
- Evaluated answers: **{answers}**
- Model candidates: **{models}**
- Current recommended baseline: **{best}**
- Current review rate: **{review_rate:.1%}**

## HCAI-DS Value
The project connects data science, AI evaluation, product thinking, responsible AI, and human-centered review operations. It is intentionally not just a model-building project; it focuses on whether AI advice can be trusted, explained, reviewed, and improved.

## Honest Boundary
The current version is a portfolio-ready research demo. It should not be described as a production system or as a real commercial LLM benchmark until real model outputs and human annotations are collected.
"""
    ONE_PAGER.write_text(one_pager, encoding="utf-8")

    html = f"""<!doctype html>
<html lang=\"en\">
<head>
  <meta charset=\"utf-8\" />
  <meta name=\"viewport\" content=\"width=device-width, initial-scale=1\" />
  <title>AI Study Advice Evaluation Platform</title>
  <style>
    body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; margin: 0; background: #f7f7fb; color: #1f2937; }}
    main {{ max-width: 980px; margin: 0 auto; padding: 56px 24px; }}
    .hero {{ background: white; border-radius: 24px; padding: 40px; box-shadow: 0 12px 40px rgba(31,41,55,.08); }}
    h1 {{ font-size: 44px; margin: 0 0 12px; line-height: 1.05; }}
    h2 {{ margin-top: 36px; }}
    .tag {{ display:inline-block; padding:8px 12px; border-radius:999px; background:#eef2ff; margin-bottom:20px; font-weight:600; }}
    .grid {{ display:grid; grid-template-columns: repeat(auto-fit,minmax(180px,1fr)); gap:16px; margin-top:24px; }}
    .card {{ background:white; border-radius:18px; padding:20px; box-shadow: 0 8px 24px rgba(31,41,55,.06); }}
    .metric {{ font-size:32px; font-weight:800; }}
    .muted {{ color:#6b7280; }}
    li {{ margin: 8px 0; }}
  </style>
</head>
<body>
<main>
  <section class=\"hero\">
    <div class=\"tag\">Human-Centered AI · Data Science · Product Evaluation</div>
    <h1>AI Study Advice Evaluation Platform</h1>
    <p class=\"muted\">A portfolio-ready HCAI-DS prototype for evaluating whether AI-generated academic and career advice is accurate, helpful, actionable, and safe enough for student decision-making.</p>
    <div class=\"grid\">
      <div class=\"card\"><div class=\"metric\">{questions}</div><div>Student scenarios</div></div>
      <div class=\"card\"><div class=\"metric\">{answers}</div><div>Evaluated answers</div></div>
      <div class=\"card\"><div class=\"metric\">{models}</div><div>Model candidates</div></div>
      <div class=\"card\"><div class=\"metric\">{review_rate:.0%}</div><div>Review workload</div></div>
    </div>
  </section>
  <h2>What it does</h2>
  <ul>
    <li>Compares multiple AI answer models with a human-centered rubric.</li>
    <li>Uses risk-aware scoring so high-impact advice is judged more strictly.</li>
    <li>Routes weak or risky answers into a review queue with suggested product fixes.</li>
    <li>Generates portfolio reports, leaderboard artifacts, and launch-readiness checks.</li>
  </ul>
  <h2>Best current baseline</h2>
  <p><strong>{best}</strong> is recommended under the current simulated demo data. This is a workflow demonstration, not a claim about real commercial LLM performance.</p>
</main>
</body>
</html>
"""
    HTML_PATH.write_text(html, encoding="utf-8")
    print(f"Created {ONE_PAGER.relative_to(ROOT)} and {HTML_PATH.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
