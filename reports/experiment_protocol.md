# Experiment Protocol

## Project Title

Human-Centered Evaluation of AI-Generated Student Advice

## Research Objective

This project evaluates how well different AI answer-generation strategies support students in academic, career, and research-planning scenarios. The focus is not only answer quality, but also risk-sensitive behavior: when advice could affect important decisions, the system should be more cautious, transparent, and actionable.

## Research Questions

1. Which model or answer strategy produces the strongest risk-weighted student advice?
2. Which types of student questions are most likely to require human review?
3. What failure patterns appear most often: generic advice, missing steps, overconfidence, possible inaccuracy, or missing source guidance?
4. Can a human-centered evaluation rubric turn model failures into product guardrails?

## Dataset

The current v3 dataset includes simulated student-advice questions and simulated model answers. It is suitable for product prototyping and methodology demonstration. External claims should be avoided until real model outputs and human annotations are added.

## Experimental Design

- Unit of analysis: one model answer to one student question.
- Independent variable: model or answer-generation strategy.
- Dependent variables: accuracy, helpfulness, clarity, actionability, risk control, overall score, risk-weighted score, review status.
- Risk segmentation: low, medium, high.
- Review rule: low overall score or weak high-risk risk control triggers human review.

## Annotation Plan

1. Generate or collect answers from at least three real models.
2. Remove model labels for blind rating when possible.
3. Ask at least two raters to score a 20–30% subset.
4. Compare disagreement and refine the rubric.
5. Use the final rubric to score the full dataset.

## Product Decision Rule

A model should not be selected only because it has the highest average score. The recommended baseline is the model with the best combination of high risk-weighted score, low review rate, strong high-risk risk-control, low overconfidence rate, and acceptable actionability.

## Limitations

- Current model outputs are simulated.
- Ratings are generated for demonstration and should be replaced with human annotations.
- The dataset is focused on student advice and should not be generalized to medical, legal, or financial advice.

## Next Experiment

The next mature experiment should compare real outputs from ChatGPT, Claude, and Gemini on the same 62 student questions using the same rubric.
