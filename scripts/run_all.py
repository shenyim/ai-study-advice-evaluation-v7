from pathlib import Path
import subprocess
import sys

from utils_io import load_evaluation_config

ROOT = Path(__file__).resolve().parents[1]
BASE_STEPS = [
    "seed_questions.py",
    "data.py",
    "eda.py",
]

POST_SCORING_STEPS = [
    "analyze_ratings.py",
    "build_review_queue.py",
    "build_leaderboard.py",
    "generate_annotation_batches.py",
    "merge_human_annotations.py",
    "check_annotation_completeness.py",
    "analyze_human_reliability.py",
    "analyze_model_differences.py",
    "check_data_quality.py",
    "build_prompt_pack.py",
    "evaluate_launch_readiness.py",
    "generate_real_model_comparison_report.py",
    "generate_research_results.py",
    "generate_final_research_report.py",
    "generate_portfolio_assets.py",
    "generate_report_summary.py",
    "run_sanity_checks.py",
]


def run_step(step: str, optional: bool = False) -> bool:
    print(f"\n=== Running {step} ===")
    try:
        subprocess.run([sys.executable, str(ROOT / "scripts" / step)], cwd=ROOT, check=True)
        return True
    except subprocess.CalledProcessError as exc:
        label = "WARNING" if optional else "ERROR"
        print(f"{label}: {step} exited with code {exc.returncode}.")
        if not optional:
            raise
        return False


def main() -> None:
    config = load_evaluation_config()
    mode = config.get("mode", "simulated")
    print(f"AI Study Advice Evaluation Platform v7 pipeline")
    print(f"Evaluation mode: {mode}")

    for step in BASE_STEPS:
        run_step(step)

    if mode == "real":
        run_step("import_real_model_answers.py", optional=True)
    else:
        run_step("generate_answers.py")

    if mode == "real" and not (ROOT / "data" / "real_model_answers_clean.csv").exists():
        print("WARNING: Real mode requested but clean real data is unavailable. Switching this run to simulated answers.")
        run_step("generate_answers.py")

    run_step("validate_real_model_answers.py", optional=True)
    run_step("create_ratings_template.py")

    if mode == "human_scored":
        print("Human-scored mode selected. Using provided scores when available.")
    run_step("fill_sample_ratings.py")

    for step in POST_SCORING_STEPS:
        optional = step in {"merge_human_annotations.py", "generate_real_model_comparison_report.py"}
        run_step(step, optional=optional)

    print("\nPipeline complete.")
    print("Key outputs:")
    print("- data/evaluated_answers.csv")
    print("- data/review_queue.csv")
    print("- reports/model_leaderboard.md")
    print("- reports/statistical_analysis.md")
    print("- reports/final_research_report.md")
    print("- reports/sanity_check_report.md")
    print("\nRun the dashboard with: streamlit run app.py")


if __name__ == "__main__":
    main()
