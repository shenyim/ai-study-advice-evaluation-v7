# Launch Checklist

This checklist defines what must be true before the project is shown as a serious portfolio demo or expanded into a real student-facing tool.

## P0: Must-have before demo

- [ ] The dashboard runs locally with `streamlit run dashboard.py`.
- [ ] `data/ratings.csv` exists and has no missing score values.
- [ ] Every evaluated answer has a model name, question id, answer text, expected risk level, and all five rubric scores.
- [ ] `reports/data_quality_report.md` has been generated.
- [ ] `reports/launch_readiness_report.md` has been generated.
- [ ] README clearly states which results are simulated and which are real.
- [ ] High-risk cases are flagged with review priority.
- [ ] The project does not claim that simulated results prove real model performance.

## P1: Stronger portfolio version

- [ ] Add real outputs from at least two real LLMs.
- [ ] Score at least 30 real model answers manually.
- [ ] Add one short reflection on disagreement between models.
- [ ] Add one screenshot of the dashboard to the README.
- [ ] Add a short demo video or walkthrough script.

## P2: Research-ready version

- [ ] Use two or more human raters.
- [ ] Track inter-rater disagreement.
- [ ] Add consent/privacy notes if real student questions are used.
- [ ] Add a clear sampling strategy for questions.
- [ ] Write a short workshop-paper style report.
