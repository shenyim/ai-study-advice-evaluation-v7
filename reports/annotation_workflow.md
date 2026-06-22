# Human Annotation Workflow

This project supports a multi-rater evaluation workflow for AI-generated student advice.

1. Run `python scripts/generate_annotation_batches.py` to create `data/human_annotation_template.csv` and rater batch files.
2. Give each rater a CSV with the same rubric columns and a unique `rater_id`.
3. Ask raters to score each answer from 1 to 5 for usefulness, specificity, actionability, empathy, risk control, and overall quality.
4. Ask raters to assign one failure type from `reports/failure_taxonomy.md`.
5. Save completed files in `data/annotation_batches/` with `completed` in the filename, or use the completed sample for a demo run.
6. Run `python scripts/merge_human_annotations.py`.
7. Run `python scripts/check_annotation_completeness.py`.
8. Run `python scripts/analyze_human_reliability.py`.

The workflow is intentionally conservative: human scores are useful only when coverage, rater consistency, and rubric interpretation are visible.
