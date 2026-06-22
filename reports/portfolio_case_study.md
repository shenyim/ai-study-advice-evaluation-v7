# Portfolio Case Study: AI Study Advice Evaluation Platform

## One-Line Summary

I built a human-centered AI evaluation platform that compares student-advice models using risk-aware scoring, review gates, and failure taxonomy analysis.

## Problem

Students increasingly use AI for academic planning, career decisions, coding help, and research advice. However, a polished AI answer is not always a safe or useful answer. In high-impact scenarios such as PhD planning, course selection, or policy interpretation, AI systems need stronger uncertainty handling, clearer next steps, and better review mechanisms.

## Product Idea

This project is an internal AI quality layer for student-advice systems. Instead of only generating answers, it evaluates model outputs across five human-centered dimensions: accuracy, helpfulness, clarity, actionability, and risk control.

## My Role

- Designed the product concept and evaluation workflow.
- Created a structured student-advice scenario dataset.
- Built a multi-model comparison dashboard with Streamlit.
- Defined a risk-sensitive rubric and quality gates.
- Added failure taxonomy, review queue logic, and product roadmap documentation.

## Technical Stack

Python, pandas, Streamlit, matplotlib, CSV-based evaluation pipeline, and modular scripts for data seeding, answer generation, rating analysis, report generation, and human annotation workflow.

## Key Features

### Model Comparison
The dashboard compares multiple models by average score, risk-weighted score, review rate, and high-risk review rate.

### Risk-Sensitive Scoring
High-risk questions place more weight on risk control. This prevents a model from looking good only because its answers are fluent.

### Review Queue
Answers are flagged for review when they fail minimum quality gates, especially on high-risk questions.

### Failure Taxonomy
The system tracks whether failures come from missing steps, generic advice, overconfidence, possible inaccuracy, or missing source guidance.

### Case Review Console
Reviewers can inspect each question, model answer, scores, notes, and suggested product fix.

## What I Learned

This project showed that AI evaluation should not rely only on average accuracy. In student-facing systems, the cost of a mistake depends heavily on context. A weak answer to a low-risk coding question is different from a weak answer about graduate school planning. A mature AI product needs risk-aware evaluation, human review, and continuous improvement loops.

## Future Improvements

- Replace simulated outputs with real model outputs.
- Add multi-rater human annotation and inter-rater agreement.
- Add prompt version tracking and model version tracking.
- Expand the dataset to more student populations.
- Add retrieval-based source verification for policy-sensitive advice.

## Resume Bullet

Built a Streamlit-based human-centered AI evaluation platform for student-advice systems, comparing model outputs with risk-weighted scoring, quality gates, review queue logic, and failure taxonomy analysis.
