# Statistical Analysis

This is a lightweight statistical layer for a portfolio/research prototype. It uses bootstrap confidence intervals instead of claiming formal production-grade inference.

## Model Leaderboard

| model_name   |   answers |   avg_weighted |   avg_overall |   review_rate |
|:-------------|----------:|---------------:|--------------:|--------------:|
| Claude       |         1 |          4.18  |          4.18 |             0 |
| ChatGPT      |         2 |          3.845 |          3.87 |            50 |
| Gemini       |         1 |          3.69  |          3.74 |           100 |

## Pairwise Differences

| metric         | model_a   | model_b   |   mean_a |   mean_b |   mean_diff_a_minus_b |   bootstrap_ci_2_5 |   bootstrap_ci_97_5 |   effect_size_cohens_d | ci_crosses_zero   | evidence_strength   |
|:---------------|:----------|:----------|---------:|---------:|----------------------:|-------------------:|--------------------:|-----------------------:|:------------------|:--------------------|
| weighted_score | Claude    | Gemini    |    4.18  |     3.69 |                 0.49  |               0.49 |                0.49 |                    nan | False             | strong              |
| weighted_score | ChatGPT   | Gemini    |    3.845 |     3.69 |                 0.152 |              -0.1  |                0.41 |                    nan | True              | weak                |
| weighted_score | ChatGPT   | Claude    |    3.845 |     4.18 |                -0.338 |              -0.59 |               -0.08 |                    nan | False             | strong              |

## Category-Level Differences

| category     | metric         | model_a   | model_b   |   mean_a |   mean_b |   mean_diff_a_minus_b |   bootstrap_ci_2_5 |   bootstrap_ci_97_5 |   effect_size_cohens_d | ci_crosses_zero   | evidence_strength   |
|:-------------|:---------------|:----------|:----------|---------:|---------:|----------------------:|-------------------:|--------------------:|-----------------------:|:------------------|:--------------------|
| phd_planning | weighted_score | ChatGPT   | Gemini    |     3.59 |     3.69 |                 -0.1  |              -0.1  |               -0.1  |                    nan | False             | moderate            |
| programming  | weighted_score | ChatGPT   | Claude    |     4.1  |     4.18 |                 -0.08 |              -0.08 |               -0.08 |                    nan | False             | moderate            |

## High-Risk-Only Differences

| metric         | model_a   | model_b   |   mean_a |   mean_b |   mean_diff_a_minus_b |   bootstrap_ci_2_5 |   bootstrap_ci_97_5 |   effect_size_cohens_d | ci_crosses_zero   | evidence_strength   |
|:---------------|:----------|:----------|---------:|---------:|----------------------:|-------------------:|--------------------:|-----------------------:|:------------------|:--------------------|
| weighted_score | ChatGPT   | Gemini    |     3.59 |     3.69 |                  -0.1 |               -0.1 |                -0.1 |                    nan | False             | moderate            |

## Interpretation

The current best release-candidate model by risk-weighted score is **Claude**.
A difference is directionally meaningful when the average gap is non-trivial and the confidence interval mostly supports the same direction.
If a bootstrap confidence interval crosses zero, evidence is weak or mixed for that pair under the current sample.
Evidence labels are weak, moderate, or strong diagnostics for this dataset; they are not formal large-scale benchmark claims.
This is not a formal large-scale benchmark unless the dataset is expanded with real model outputs, fixed prompts, and reliable human scoring.