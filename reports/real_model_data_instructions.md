# Real Model Data Collection Instructions

Use `data/real_model_answers_template.csv` to collect outputs from ChatGPT, Claude, Gemini, Perplexity, Llama, or other candidates.

Required fields:

- `question_id`: must match `data/student_questions_clean.csv`.
- `category`: question category from the cleaned dataset.
- `risk_level`: one of `low`, `medium`, or `high`.
- `student_question`: exact question shown to the model.
- `model_name`: readable model label such as `ChatGPT`, `Claude`, `Gemini`, `Perplexity`, or `Llama`.
- `model_version`: specific version if available.
- `prompt_version`: prompt protocol label, for example `prompt_v1`.
- `answer_text`: complete model answer.
- `collection_date`: date collected.
- `collector_notes`: prompt deviations, UI settings, temperature, or caveats.

Recommended protocol:

1. Use the same prompt template for every model.
2. Keep temperature and system instructions as consistent as each platform allows.
3. Do not edit model answers except to remove private information.
4. Record model version and date because model behavior can change.
5. Run `python scripts/import_real_model_answers.py`.
6. Switch `config/evaluation_mode.json` to `"mode": "real"`.
7. Run `python scripts/run_all.py`.

The real-model report should be interpreted cautiously. Results depend on sample size, prompt setup, rater reliability, and the exact model versions collected.

