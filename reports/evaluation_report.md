# Evaluation Report

## Summary

This report summarizes a simulated evaluation of AI-generated student advice across 62 student questions, 3 model candidates, and 186 evaluated answers.

The project is designed as a prototype of an internal AI quality evaluation platform for academic, career, research, and study-advice systems.

## Dataset

The dataset includes questions across programming, statistics, data science, AI evaluation, responsible AI, HCI, product strategy, research methods, PhD planning, and career planning.

Each question includes:

- question ID
- question text
- category
- difficulty
- student background
- expected risk level

## Models Compared

The current prototype compares three simulated model profiles:

1. `Balanced_GPT`: safer, more complete, more explicit about verification.
2. `Concise_Model`: shorter and clearer, but often less actionable.
3. `Overconfident_Model`: fluent but risky because it gives advice with too much certainty.

## Rubric

Each answer is scored from 1 to 5 on:

- Accuracy
- Helpfulness
- Clarity
- Actionability
- Risk Control

## Main Finding

The safer balanced model performs best under risk-sensitive scoring. The overconfident model performs worst because it repeatedly fails risk-control gates, especially for high-risk academic and career questions.

## Product Interpretation

The most important product insight is that overall answer quality is not enough. A model can sound fluent and still be unsafe for student decision-making.

A mature AI advising product should therefore include:

- risk classification
- stricter high-risk answer rules
- human review queue
- model comparison dashboard
- failure taxonomy
- product guardrail iteration

## Recommended Next Iteration

1. Replace simulated answers with real LLM outputs.
2. Add real or semi-real student questions with privacy protection.
3. Recruit 2–3 human raters.
4. Add inter-rater agreement.
5. Convert recurring failure patterns into answer templates and guardrails.


## v3 Research-Ops Upgrade

The project now includes a workflow for moving from simulated outputs to real model comparison. The added files support real answer import, human annotation, data quality checks, and portfolio-ready reporting. This makes the project more credible as an HCAI-DS artifact because it demonstrates not only a dashboard, but also an evaluation operation: dataset creation, rubric design, model comparison, human review, and product iteration.

Important caveat: the included ratings are still prototype ratings. A mature study should replace them with human ratings from at least two reviewers and report disagreement before making strong claims about real model performance.
