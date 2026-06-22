# Product Requirements: AI Study Advice Evaluation Platform

## Product Vision

Build an internal evaluation platform that helps teams evaluate, compare, and improve AI-generated academic and career advice before it reaches students.

The product should not only ask, "Is the answer good?" It should ask, "Is this answer safe and useful enough for this specific student decision?"

## Target Users

1. AI product teams building education or advising assistants.
2. Academic support teams reviewing AI-generated study guidance.
3. HCI / HCAI researchers studying student trust, risk, and AI advice quality.
4. Data scientists monitoring model behavior across topics and risk levels.

## Core User Problems

- AI advice can sound confident even when it is incomplete or risky.
- Traditional model metrics do not capture student-facing usefulness.
- High-risk academic and career advice needs stricter review than low-risk programming help.
- Teams need a structured way to compare model candidates.
- Product teams need to turn evaluation findings into guardrails and product changes.

## MVP Scope

### Included

- 62 simulated student questions.
- 3 simulated model candidates.
- 186 evaluated answers.
- Human-centered rubric dimensions.
- Risk-sensitive weighted score.
- Quality gates.
- Model comparison scorecard.
- Case review console.
- Failure taxonomy.
- Exportable filtered data.

### Out of Scope

- Real student data collection.
- Real LLM API calls.
- Authentication.
- Production database.
- Multi-rater reviewer management.
- Automated factuality verification.

## Evaluation Dimensions

1. Accuracy
2. Helpfulness
3. Clarity
4. Actionability
5. Risk Control

## Risk-sensitive Scoring Logic

Low-risk questions mainly emphasize usefulness and clarity.

Medium-risk questions balance quality and safety.

High-risk questions place more weight on risk control because poor advice can affect academic planning, PhD applications, career decisions, or university-policy interpretation.

## Quality Gates

An answer enters the review queue if:

- Overall score < 4.0
- High-risk risk control < 4.5
- High-risk actionability < 4.0

## Success Metrics

| Metric | Target |
|---|---|
| Overall average score | >= 4.2 |
| Risk-weighted score | >= 4.3 |
| High-risk risk-control score | >= 4.5 |
| Review rate | Lower without weakening safety |
| Overconfident error rate | Decrease over iterations |
| Missing-steps error rate | Decrease after answer-template improvements |

## Product Roadmap

### P0: Make evaluation realistic

- Add real model outputs.
- Add more student questions.
- Improve high-risk guardrail requirements.

### P1: Add research depth

- Add multi-rater scoring.
- Add inter-rater agreement.
- Add qualitative coding for reviewer notes.

### P2: Add production behavior

- Add database backend.
- Add reviewer workflow.
- Add model version tracking.
- Add continuous monitoring.

## Research Value

This project fits Human-Centered AI and Data Science because it connects:

- AI evaluation
- Human-AI interaction
- Responsible AI
- Student decision-making
- Data visualization
- Product analytics
- Qualitative failure analysis

## Portfolio Positioning

This should be presented as an HCAI-DS evaluation platform, not a simple dashboard.

Best project title:

> Human-Centered Evaluation Platform for AI Study Advice

Best short description:

> A Streamlit-based AI evaluation platform that compares model-generated student advice using human-centered quality metrics, risk-aware scoring, and review workflows.
