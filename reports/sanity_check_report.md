# Sanity Check Report

| check                                               | status   | detail                                                                     |
|:----------------------------------------------------|:---------|:---------------------------------------------------------------------------|
| Folder exists: data                                 | PASS     | data                                                                       |
| Folder exists: reports                              | PASS     | reports                                                                    |
| Folder exists: figures                              | PASS     | figures                                                                    |
| Folder exists: config                               | PASS     | config                                                                     |
| Evaluation mode config exists                       | PASS     | config/evaluation_mode.json                                                |
| Evaluation mode is valid                            | PASS     | real                                                                       |
| Questions include question_id                       | PASS     | data/student_questions_clean.csv                                           |
| Question IDs are unique                             | PASS     | data/student_questions_clean.csv                                           |
| Ratings required columns exist                      | PASS     | all present                                                                |
| Scores are within 1-5                               | PASS     | accuracy, helpfulness, clarity, actionability, risk_control, overall_score |
| Generated report exists: model_leaderboard.md       | PASS     | reports/model_leaderboard.md                                               |
| Generated report exists: review_queue_report.md     | PASS     | reports/review_queue_report.md                                             |
| Generated report exists: statistical_analysis.md    | PASS     | reports/statistical_analysis.md                                            |
| Generated report exists: launch_readiness_report.md | PASS     | reports/launch_readiness_report.md                                         |
| Generated report exists: final_research_report.md   | PASS     | reports/final_research_report.md                                           |

Overall status: **PASS**
