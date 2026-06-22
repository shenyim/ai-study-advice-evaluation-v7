# AI Study Advice Evaluation Platform

## Abstract

This project is a human-centered AI evaluation platform for student-advice systems. It supports simulated and real model outputs, risk-aware scoring, human annotation, reliability analysis, bootstrap model comparison, launch readiness checks, and a Streamlit dashboard.

## Introduction

Student-facing AI advice can sound polished while still being vague, overconfident, or unsafe for academic and career decisions. This project evaluates advice quality as a human-centered product and research problem.

## Research Question

How can AI-generated student advice be evaluated across quality, actionability, empathy, and risk control while producing evidence useful for model selection and product iteration?

## System Overview

Active evaluation mode: **real**.
The pipeline creates or imports model answers, scores them, builds a review backlog, analyzes human reliability, compares models statistically, and generates research and portfolio outputs.

## Dataset

- Unique questions: **2**
- Evaluated answers: **4**
- Model candidates: **3**

## Evaluation Rubric

The scoring layer uses accuracy, helpfulness, clarity, actionability, and risk control. Human annotation maps usefulness, specificity, actionability, empathy, and risk control into the same analysis layer for compatibility.

## Human Annotation Workflow

The workflow includes annotation templates, rater batches, merge logic, completeness checks, rater coverage, and reliability diagnostics.

## Model Comparison Method

Models are compared with average overall score, risk-weighted score, review rate, P0/P1/P2 pressure, high-risk performance, failure taxonomy, and bootstrap confidence intervals.

## Results

- Average overall score: **3.92**
- Review rate: **50.0%**

| model_name   |   evaluated_answers |   unique_questions |   overall_score |   weighted_score |   review_rate |   p0_rate |   high_risk_coverage |   accuracy |   helpfulness |   clarity |   actionability |   risk_control |   release_candidate_score |
|:-------------|--------------------:|-------------------:|----------------:|-----------------:|--------------:|----------:|---------------------:|-----------:|--------------:|----------:|----------------:|---------------:|--------------------------:|
| Claude       |                   1 |                  1 |            4.18 |            4.18  |           0   |       0   |                    0 |       4.3  |          4.1  |       4   |            4.3  |            4.2 |                     4.389 |
| ChatGPT      |                   2 |                  2 |            3.87 |            3.845 |           0.5 |       0.5 |                    1 |       3.95 |          3.85 |       4   |            3.75 |            3.8 |                     3.5   |
| Gemini       |                   1 |                  1 |            3.74 |            3.69  |           1   |       1   |                    1 |       3.8  |          3.8  |       4.1 |            3.4  |            3.6 |                     2.75  |

## Human Reliability Findings

| dimension     |   icc_1_1 |   krippendorff_alpha_approx |   mean_abs_disagreement |   median_abs_disagreement |   within_0_5_rate |   within_1_0_rate |
|:--------------|----------:|----------------------------:|------------------------:|--------------------------:|------------------:|------------------:|
| accuracy      |     0.048 |                       0.042 |                   0.375 |                      0.35 |               100 |               100 |
| helpfulness   |     0.048 |                       0.042 |                   0.375 |                      0.35 |               100 |               100 |
| clarity       |     0.429 |                       0.391 |                   0.4   |                      0.4  |               100 |               100 |
| actionability |     0.239 |                       0.212 |                   0.35  |                      0.35 |               100 |               100 |
| risk_control  |     0.429 |                       0.391 |                   0.4   |                      0.4  |               100 |               100 |
| overall_score |     0.798 |                       0.772 |                   0.11  |                      0.05 |               100 |               100 |

## Statistical Evidence

| metric         | model_a   | model_b   |   mean_a |   mean_b |   mean_diff_a_minus_b |   bootstrap_ci_2_5 |   bootstrap_ci_97_5 |   effect_size_cohens_d | ci_crosses_zero   | evidence_strength   |
|:---------------|:----------|:----------|---------:|---------:|----------------------:|-------------------:|--------------------:|-----------------------:|:------------------|:--------------------|
| weighted_score | Claude    | Gemini    |    4.18  |     3.69 |                 0.49  |               0.49 |                0.49 |                    nan | False             | strong              |
| weighted_score | ChatGPT   | Gemini    |    3.845 |     3.69 |                 0.152 |              -0.1  |                0.41 |                    nan | True              | weak                |
| weighted_score | ChatGPT   | Claude    |    3.845 |     4.18 |                -0.338 |              -0.59 |               -0.08 |                    nan | False             | strong              |

## Product Implications

The current review backlog contains **2** open items.
The backlog links failure modes to owners, root-cause hypotheses, and recommended fixes.

## Launch Readiness

Launch readiness is assessed through configured gates, but passing demo gates does not imply real deployment readiness.

## Limitations

This is a portfolio and research demo, not a deployed student-advice product. Results depend on sample size, prompt setup, model version, rubric design, rater reliability, and dataset representativeness.

## Future Work

Expand real model collection, recruit independent raters, improve rubric examples, evaluate prompt interventions, add privacy controls, and test whether students understand and trust risk-aware advice appropriately.

## Portfolio Summary

The project demonstrates applied AI evaluation, human-centered data science, product analytics, research operations, statistical evidence, and responsible AI judgment.
