# Research Results and Discussion

## Research Question

How can a human-centered evaluation workflow compare AI-generated student advice across usefulness, actionability, and risk control?

## Method Summary

The system evaluates student-advice answers using a five-dimension rubric: accuracy, helpfulness, clarity, actionability, and risk control. Scores are converted into risk-weighted product metrics and review priorities.

## Key Findings

- The strongest current model candidate is **Claude** under the risk-weighted scoring setup.
- The weakest evaluation dimension is **actionability**, which should drive the next prompt/product iteration.
- The current review rate is **50.0%**, meaning the system still finds a meaningful number of cases requiring human review.
- The P0 rate is **50.0%**, which is the main launch-readiness blocker for a real student-facing system.

## HCAI Interpretation

The central product lesson is that advice quality cannot be reduced to whether an answer sounds fluent. In student-advice settings, the most important failures are often subtle: overconfidence, missing caveats, vague next steps, or weak escalation guidance for high-impact decisions.

## Limitations

- The current default dataset uses simulated model outputs.
- Human annotation examples are included as workflow scaffolding, not final evidence.
- The rubric needs real rater calibration before making strong empirical claims.
- Student privacy, consent, and institutional deployment constraints are outside the demo scope.

## Next Iteration

1. Replace simulated model outputs with real outputs from multiple LLMs.
2. Recruit 2–3 raters and compute inter-rater reliability.
3. Run pairwise model comparison using human-scored results.
4. Convert top failure modes into prompt rules, UI warnings, and review policies.