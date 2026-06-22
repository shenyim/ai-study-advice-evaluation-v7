# AI Study Advice Evaluation Platform

A human-centered AI evaluation platform for student-advice systems.

This project evaluates whether AI-generated academic, research, and career advice is useful, specific, actionable, empathetic, and risk-aware. It supports simulated model answers, imported real model answers, human annotation workflows, model comparison, statistical evidence, review queues, launch readiness checks, and a Streamlit dashboard.

> This project is a portfolio and research demo, not a deployed student-advice product.

## Why This Matters

Student-facing AI advice can sound confident even when it is vague, misleading, or unsafe for high-impact decisions. This project treats AI advice quality as a human-centered evaluation and product governance problem, not just a chatbot output problem.

## Key Features

- Simulated evaluation mode that always runs end-to-end.
- Real model answer import workflow for ChatGPT, Claude, Gemini, Perplexity, Llama, or open-source candidates.
- Human annotation templates, multi-rater batches, merge scripts, and completeness reports.
- Inter-rater reliability analysis with pairwise disagreement, percent agreement, rater bias, and an approximate Krippendorff-style diagnostic.
- Risk-aware scoring and launch gates for high-risk student advice.
- Bootstrap pairwise model comparison with confidence intervals, effect sizes, category-level analysis, and high-risk-only analysis.
- Product review queue with P0/P1/P2 priorities, owners, root-cause hypotheses, and recommended fixes.
- Final research report, portfolio pitches, resume bullets, and GitHub-ready project positioning.
- Streamlit dashboard for overview, leaderboard, real model evaluation, annotation, statistics, review queue, case review, launch readiness, and portfolio summary.

## Project Architecture

```text
data/
  student_questions_clean.csv
  simulated_model_answers.csv
  real_model_answers_template.csv
  real_model_answers_clean.csv
  human_annotation_template.csv
  ratings.csv
  evaluated_answers.csv
  review_queue.csv

scripts/
  run_all.py
  generate_answers.py
  import_real_model_answers.py
  validate_real_model_answers.py
  generate_annotation_batches.py
  merge_human_annotations.py
  check_annotation_completeness.py
  analyze_human_reliability.py
  analyze_model_differences.py
  build_review_queue.py
  build_leaderboard.py
  generate_real_model_comparison_report.py
  generate_final_research_report.py
  run_sanity_checks.py

reports/
  final_research_report.md
  model_leaderboard.md
  statistical_analysis.md
  real_model_comparison_report.md
  human_reliability_report.md
  annotation_completeness_report.md
  review_queue_report.md
  launch_readiness_report.md
  resume_bullets.md

figures/
  risk_weighted_score_by_model.png
  review_rate_by_model.png
  failure_type_distribution.png
  high_risk_performance_by_model.png
  bootstrap_confidence_intervals.png
```

## How To Run

Install dependencies:

```bash
pip install -r requirements.txt
```

Run the full pipeline:

```bash
python scripts/run_all.py
```

Run the dashboard:

```bash
streamlit run app.py
```

## Evaluation Workflow

1. Generate or validate the student-question dataset.
2. Generate simulated model answers or import real model answers.
3. Create a scoring template.
4. Score answers or load human-scored annotations.
5. Analyze scores and build model leaderboard.
6. Build review queue and launch readiness reports.
7. Analyze human reliability when annotations exist.
8. Run bootstrap model-difference analysis.
9. Generate final research and portfolio reports.
10. Run sanity checks.

## Simulated vs Real Model Mode

The active mode is controlled by `config/evaluation_mode.json`.

```json
{
  "mode": "simulated",
  "input_file": "data/simulated_model_answers.csv",
  "output_file": "data/evaluated_answers.csv",
  "allowed_modes": ["simulated", "real", "human_scored"]
}
```

Modes:

- `simulated`: uses deterministic demo answers from `scripts/generate_answers.py`.
- `real`: imports and evaluates `data/real_model_answers_clean.csv`.
- `human_scored`: uses completed human annotation scores when available.

If real data is unavailable, the pipeline warns clearly and falls back to the simulated demo path.

## Dashboard Screenshots

Add screenshots here after running the dashboard:

- Overview page screenshot placeholder.
- Model leaderboard screenshot placeholder.
- Review queue screenshot placeholder.
- Case review screenshot placeholder.

## Reports Generated

- `reports/final_research_report.md`
- `reports/model_leaderboard.md`
- `reports/statistical_analysis.md`
- `reports/real_model_comparison_report.md`
- `reports/human_reliability_report.md`
- `reports/annotation_completeness_report.md`
- `reports/review_queue_report.md`
- `reports/launch_readiness_report.md`
- `reports/sanity_check_report.md`
- `reports/resume_bullets.md`
- `reports/interview_talking_points.md`

## Limitations

- The default dataset and model answers are simulated for reproducibility.
- Real model results depend on prompt setup, collection date, model version, and sampling conditions.
- Human ratings require enough independent raters before strong research claims are appropriate.
- Bootstrap intervals are useful evidence diagnostics, not a replacement for a large preregistered benchmark.
- The dashboard is a local research/product prototype, not a production reviewer system.

## Future Work

- Collect larger real model answer samples across locked prompts.
- Recruit independent human raters and improve rubric examples.
- Add privacy and consent workflows for real student questions.
- Test prompt and product interventions that reduce repeated failure modes.
- Study how students interpret risk-aware advice and uncertainty language.

## Portfolio Positioning

This project demonstrates applied AI evaluation, product data science, human-centered research operations, statistical reasoning, and responsible AI judgment. It is suitable for a GitHub portfolio, UMich MSI showcase, HCAI-DS research preparation, AI evaluation internship discussion, and PhD research interest demonstration.

