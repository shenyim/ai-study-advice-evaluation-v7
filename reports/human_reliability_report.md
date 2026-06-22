# Human Reliability Report

Source file: `data/human_annotation_merged.csv`
Unique answers scored: **4**
Unique raters: **2**

## Reliability Summary

| dimension     |   icc_1_1 |   krippendorff_alpha_approx |   mean_abs_disagreement |   median_abs_disagreement |   within_0_5_rate |   within_1_0_rate |
|:--------------|----------:|----------------------------:|------------------------:|--------------------------:|------------------:|------------------:|
| accuracy      |     0.048 |                       0.042 |                   0.375 |                      0.35 |               100 |               100 |
| helpfulness   |     0.048 |                       0.042 |                   0.375 |                      0.35 |               100 |               100 |
| clarity       |     0.429 |                       0.391 |                   0.4   |                      0.4  |               100 |               100 |
| actionability |     0.239 |                       0.212 |                   0.35  |                      0.35 |               100 |               100 |
| risk_control  |     0.429 |                       0.391 |                   0.4   |                      0.4  |               100 |               100 |
| overall_score |     0.798 |                       0.772 |                   0.11  |                      0.05 |               100 |               100 |

## Rater Severity / Leniency

| rater_id   | dimension     |   mean_score |   mean_offset_vs_item_mean |   rated_answers |
|:-----------|:--------------|-------------:|---------------------------:|----------------:|
| R1         | accuracy      |        4.35  |                     -0.087 |               4 |
| R1         | actionability |        4.275 |                     -0.1   |               4 |
| R1         | clarity       |        4.4   |                      0     |               4 |
| R1         | helpfulness   |        4.35  |                     -0.087 |               4 |
| R1         | overall_score |        4.355 |                     -0.055 |               4 |
| R1         | risk_control  |        4.4   |                      0     |               4 |
| R2         | accuracy      |        4.525 |                      0.087 |               4 |
| R2         | actionability |        4.475 |                      0.1   |               4 |
| R2         | clarity       |        4.4   |                      0     |               4 |
| R2         | helpfulness   |        4.525 |                      0.087 |               4 |
| R2         | overall_score |        4.465 |                      0.055 |               4 |
| R2         | risk_control  |        4.4   |                      0     |               4 |

## Interpretation

Overall-score reliability is **0.798**, which is best treated as **strong agreement**.
The most reliable dimension in this run is **overall_score** by within-one-point agreement.
The most subjective dimension is **accuracy**; this is the first place to tighten rubric examples and rater training.
Percent agreement within ±1 point is usually easier to interpret than a single reliability coefficient for early rubric pilots.
The Krippendorff-style alpha value here is an approximation for interval-style scores and should be treated as a directional diagnostic, not a formal publication-grade estimate.

## Product Meaning

This report prevents the project from pretending that human scores are automatically objective. A mature HCAI evaluation system must measure rater disagreement, not hide it.

## Next Step

Replace the demo sample with `data/human_annotation_multi_rater_completed.csv` after 2–3 real raters score the same answer set.