# Final Project Report: AI Study Advice Evaluation Platform

## 1. Motivation

AI assistants are increasingly used for academic planning, study strategy, career decisions, and research preparation. These answers can look fluent even when they are incomplete, overconfident, or not specific enough for a student's context. This project addresses that gap by treating AI advice as something that needs human-centered evaluation, not just generation.

## 2. Product Goal

The goal is to build an internal evaluation platform for student-facing AI advice systems. The platform helps compare model candidates, identify risky answers, and convert evaluation findings into product guardrails.

## 3. Dataset

The prototype includes 62 student-advice scenarios across programming, statistics, machine learning, AI evaluation, responsible AI, human-AI interaction, research planning, PhD planning, career planning, product strategy, and data visualization. Each question includes category, difficulty, student background, and expected risk level.

## 4. Evaluation Rubric

Answers are scored from 1 to 5 across five dimensions: accuracy, helpfulness, clarity, actionability, and risk control. Risk control is especially important for high-risk questions, where overconfident or unsupported advice can cause real decision harm.

## 5. Risk-Aware Scoring

The platform uses risk-sensitive weights. For low-risk questions, helpfulness and clarity matter more. For high-risk questions, risk control receives a larger weight. This reflects a product reality: not all mistakes have the same cost.

## 6. Product Features

- Multi-model comparison
- Risk-weighted scorecard
- Quality gates
- Review priority labels
- Failure taxonomy
- Case review console
- Real model answer import template
- Human annotation workflow
- Data quality checks
- Launch readiness report

## 7. Current Result

The current demo dataset is simulated. Under the simulated evaluation, the balanced model is the strongest baseline because it has the best combination of weighted score and review workload. This should not be interpreted as a real benchmark result; it is a demonstration of the evaluation workflow.

## 8. Limitations

The current version uses simulated questions, simulated answers, and deterministic sample ratings. It does not yet include real users, real model APIs, multiple human raters, authentication, or a production database.

## 9. Next Step

The next milestone is to collect real outputs from ChatGPT, Claude, and Gemini using the prompt pack, then score those outputs using the human annotation sheet. That would move the project from workflow prototype to real comparative evaluation.

## 10. Portfolio Positioning

This project demonstrates HCAI-DS ability: data product thinking, AI evaluation, human-centered rubric design, risk-aware metrics, research operations, and product guardrails.

## v6 Research Evidence Layer

The latest version adds a reliability and statistical-evidence layer. The system now generates a multi-rater annotation sample, estimates human scoring consistency, compares model candidates using bootstrap confidence intervals, and produces a research-style results/discussion report. This makes the project stronger for HCAI-DS positioning because it no longer treats evaluation scores as automatically objective.
