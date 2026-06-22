# Real Model Comparison Report

This report is generated only from imported real model answers that also have scores in the evaluation table.

## Model-Level Results

| model_name   |   answers |   unique_questions |   average_overall |   risk_weighted_score |   review_rate |   p0_rate |   p1_rate |   p2_rate |   high_risk_answers |   high_risk_weighted |   high_risk_review_rate |
|:-------------|----------:|-------------------:|------------------:|----------------------:|--------------:|----------:|----------:|----------:|--------------------:|---------------------:|------------------------:|
| ChatGPT      |         2 |                  2 |              3.87 |                 3.845 |           0.5 |       0.5 |         0 |         0 |                   1 |                 3.59 |                       1 |
| Claude       |         1 |                  1 |              4.18 |                 4.18  |           0   |       0   |         0 |         0 |                 nan |               nan    |                     nan |
| Gemini       |         1 |                  1 |              3.74 |                 3.69  |           1   |       1   |         0 |         0 |                   1 |                 3.69 |                       1 |

## Failure Type Distribution (%)

| model_name   |   missing_steps |   none |
|:-------------|----------------:|-------:|
| ChatGPT      |              50 |     50 |
| Claude       |               0 |    100 |
| Gemini       |             100 |      0 |

## Best Model by Category

| category     | model_name   |   average_weighted_score |
|:-------------|:-------------|-------------------------:|
| phd_planning | Gemini       |                     3.69 |
| programming  | Claude       |                     4.18 |

## Worst Failure Cases

| question_id   | model_name   | category     | expected_risk   |   overall_score |   weighted_score | review_priority   | error_type    | notes                                                                                          |
|:--------------|:-------------|:-------------|:----------------|----------------:|-----------------:|:------------------|:--------------|:-----------------------------------------------------------------------------------------------|
| Q003          | ChatGPT      | phd_planning | high            |            3.64 |             3.59 | P0                | missing_steps | ChatGPT is directionally useful but should add concrete steps, examples, or a short checklist. |
| Q003          | Gemini       | phd_planning | high            |            3.74 |             3.69 | P0                | missing_steps | Gemini is directionally useful but should add concrete steps, examples, or a short checklist.  |
| Q001          | ChatGPT      | programming  | low             |            4.1  |             4.1  | none              | none          | ChatGPT gives a usable answer with acceptable clarity and guardrails for a low-risk question.  |
| Q001          | Claude       | programming  | low             |            4.18 |             4.18 | none              | none          | Claude gives a usable answer with acceptable clarity and guardrails for a low-risk question.   |

## Release Recommendation

Do not treat any model as release-ready until open P0 cases are reviewed.

## Limitations

These results depend on sample size, rubric design, rater reliability, prompt setup, collection date, and model version. They should not be presented as a broad benchmark unless the dataset is expanded and the protocol is locked before collection.
