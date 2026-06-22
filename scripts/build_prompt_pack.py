from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data"
CONFIG_DIR = ROOT / "config"
REPORTS_DIR = ROOT / "reports"
QUESTIONS_PATH = DATA_DIR / "student_questions_clean.csv"
TEMPLATE_PATH = CONFIG_DIR / "prompt_template.md"
OUT_MD = REPORTS_DIR / "real_model_prompt_pack.md"
OUT_CSV = DATA_DIR / "real_model_prompt_pack.csv"

MODELS_TO_COLLECT = ["ChatGPT_real", "Claude_real", "Gemini_real"]


def main() -> None:
    REPORTS_DIR.mkdir(exist_ok=True)
    questions = pd.read_csv(QUESTIONS_PATH)
    template = TEMPLATE_PATH.read_text(encoding="utf-8")
    rows = []
    md_parts = ["# Real Model Prompt Pack\n", "Use this pack to collect real model outputs in a consistent way. Copy one prompt at a time into each target model, then paste the answer into `data/real_model_answers_template.csv`.\n"]
    for _, row in questions.iterrows():
        prompt = (
            template
            .replace("{{question_text}}", str(row["question_text"]))
            .replace("{{student_background}}", str(row["student_background"]))
            .replace("{{expected_risk}}", str(row["expected_risk"]))
        )
        md_parts.append(f"\n## {row['question_id']} · {row['category']} · risk={row['expected_risk']}\n")
        md_parts.append("```text\n" + prompt.strip() + "\n```\n")
        for model in MODELS_TO_COLLECT:
            rows.append({
                "question_id": row["question_id"],
                "model_name": model,
                "category": row["category"],
                "expected_risk": row["expected_risk"],
                "prompt_version": "v1_student_advice",
                "prompt_text": prompt.strip(),
                "answer_text": ""
            })
    OUT_MD.write_text("\n".join(md_parts), encoding="utf-8")
    pd.DataFrame(rows).to_csv(OUT_CSV, index=False)
    print(f"Created {OUT_MD.relative_to(ROOT)}")
    print(f"Created {OUT_CSV.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
