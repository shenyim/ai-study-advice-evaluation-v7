import json

import pandas as pd

from utils_io import EVALUATION_MODE_PATH, load_evaluation_config
from utils_paths import CONFIG_DIR, DATA_DIR, FIGURES_DIR, REPORTS_DIR, ensure_project_dirs, rel
from utils_reports import md_table, write_markdown


REPORT_PATH = REPORTS_DIR / "sanity_check_report.md"


def check(condition: bool, name: str, detail: str, rows: list[dict]) -> None:
    rows.append({"check": name, "status": "PASS" if condition else "FAIL", "detail": detail})


def main() -> None:
    ensure_project_dirs()
    rows = []
    for folder in [DATA_DIR, REPORTS_DIR, FIGURES_DIR, CONFIG_DIR]:
        check(folder.exists(), f"Folder exists: {rel(folder)}", rel(folder), rows)

    config = load_evaluation_config()
    check(EVALUATION_MODE_PATH.exists(), "Evaluation mode config exists", rel(EVALUATION_MODE_PATH), rows)
    check(config.get("mode") in config.get("allowed_modes", []), "Evaluation mode is valid", str(config.get("mode")), rows)

    questions_path = DATA_DIR / "student_questions_clean.csv"
    if questions_path.exists():
        questions = pd.read_csv(questions_path)
        check("question_id" in questions.columns, "Questions include question_id", rel(questions_path), rows)
        check(not questions.get("question_id", pd.Series(dtype=str)).duplicated().any(), "Question IDs are unique", rel(questions_path), rows)
    else:
        check(False, "Questions file exists", rel(questions_path), rows)

    ratings_path = DATA_DIR / "ratings.csv"
    if ratings_path.exists():
        ratings = pd.read_csv(ratings_path)
        required = ["question_id", "model_name", "answer_text", "overall_score"]
        missing = [col for col in required if col not in ratings.columns]
        check(not missing, "Ratings required columns exist", ", ".join(missing) or "all present", rows)
        if "answer_id" in ratings.columns:
            check(not ratings["answer_id"].duplicated().any(), "Answer IDs are unique", rel(ratings_path), rows)
        score_cols = [col for col in ["accuracy", "helpfulness", "clarity", "actionability", "risk_control", "overall_score"] if col in ratings.columns]
        valid_scores = True
        for col in score_cols:
            values = pd.to_numeric(ratings[col], errors="coerce")
            valid_scores = valid_scores and bool(values.dropna().between(1, 5).all())
        check(valid_scores, "Scores are within 1-5", ", ".join(score_cols), rows)
    else:
        check(False, "Ratings file exists", rel(ratings_path), rows)

    required_reports = [
        REPORTS_DIR / "model_leaderboard.md",
        REPORTS_DIR / "review_queue_report.md",
        REPORTS_DIR / "statistical_analysis.md",
        REPORTS_DIR / "launch_readiness_report.md",
        REPORTS_DIR / "final_research_report.md",
    ]
    for report in required_reports:
        check(report.exists(), f"Generated report exists: {report.name}", rel(report), rows)

    result = pd.DataFrame(rows)
    lines = [
        "# Sanity Check Report",
        "",
        md_table(result, max_rows=80),
        "",
        f"Overall status: **{'PASS' if (result['status'] == 'PASS').all() else 'CHECK FAILURES'}**",
    ]
    write_markdown(REPORT_PATH, lines)
    print(f"Wrote {rel(REPORT_PATH)}")
    if not (result["status"] == "PASS").all():
        print("WARNING: Some sanity checks failed. See reports/sanity_check_report.md.")


if __name__ == "__main__":
    main()
