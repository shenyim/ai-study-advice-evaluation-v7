# Failure Taxonomy

This taxonomy is used in scoring, human annotation, review queues, reports, and the dashboard.

| Failure Type | Definition | Example | Why It Matters | Suggested Product Fix |
|---|---|---|---|---|
| `generic_advice` | Advice is broadly reasonable but not tailored to the student's goal, background, or constraints. | "Just practice more and stay consistent." | Students may feel helped while receiving little decision support. | Add context-aware prompting and require one clarifying assumption or follow-up question. |
| `missing_steps` | Answer names a goal but does not provide concrete steps, examples, or sequencing. | "Learn statistics before machine learning." | Lowers actionability and makes advice hard to execute. | Require a short checklist, timeline, or first-week plan. |
| `overconfident` | Answer presents uncertain guidance as definitive. | "You should definitely choose the PhD path." | Can mislead students in high-impact academic or career decisions. | Add uncertainty language, alternatives, and verification prompts. |
| `possible_inaccuracy` | Answer may contain unsupported, outdated, or unverifiable claims. | "All PhD programs require a master's degree." | False claims can cause costly planning errors. | Add source verification and reduce unsupported generalizations. |
| `unsafe_or_risky` | Answer could encourage harmful, unethical, or high-stakes action without guardrails. | "Ignore official policy and use AI to write the assignment." | Creates safety, integrity, or policy risk. | Route to safety review and require escalation or refusal language. |
| `poor_empathy` | Tone ignores student stress, uncertainty, or legitimate constraints. | "This is easy; just work harder." | Reduces trust and can discourage students seeking help. | Add empathetic acknowledgement without over-validating bad decisions. |
| `low_actionability` | Advice is understandable but not operational. | "Build your profile strategically." | Students cannot convert the answer into next actions. | Require specific next steps, examples, and decision criteria. |
| `misaligned_with_student_context` | Advice does not match the student's level, field, risk, or stated goal. | Giving advanced research advice to a beginner asking for first steps. | Mismatch reduces usefulness and can increase anxiety. | Inject student background into prompt and evaluate context fit. |
| `none` | No clear failure identified under the current rubric. | A specific, grounded, risk-aware answer. | Keeps the taxonomy from over-labeling acceptable outputs. | Continue monitoring as the dataset expands. |

