from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data"
QUESTIONS_PATH = DATA_DIR / "student_questions_clean.csv"
ANSWERS_PATH = DATA_DIR / "ai_answers.csv"
SIMULATED_ANSWERS_PATH = DATA_DIR / "simulated_model_answers.csv"

MODEL_PROFILES = {
    "Balanced_GPT": {
        "style": "balanced",
        "prefix": "A strong answer should start by clarifying the goal, then give practical next steps.",
    },
    "Concise_Model": {
        "style": "concise",
        "prefix": "Here is the short answer.",
    },
    "Overconfident_Model": {
        "style": "overconfident",
        "prefix": "The answer is straightforward and you should follow this path.",
    },
}

CATEGORY_GUIDANCE = {
    "programming": "Build the skill through small exercises, debugging practice, and one visible project.",
    "statistics": "Focus on concepts, formulas only when needed, and repeated practice with real questions.",
    "phd_planning": "Check program expectations, build research evidence, and ask faculty or advisors before making final decisions.",
    "ai_learning": "Use AI as a support tool, but keep enough technical understanding to verify and debug its output.",
    "data_science": "Start from the data problem, inspect data quality, document assumptions, and validate results.",
    "career_planning": "Compare options using goals, constraints, skill gaps, evidence, and advice from mentors.",
    "ai_evaluation": "Define a rubric, collect representative test cases, score outputs, and analyze failure modes.",
    "machine_learning": "Prepare the prerequisites, understand evaluation metrics, and practice on small datasets before scaling up.",
    "research_planning": "Turn a broad topic into a specific research question, method, dataset, and contribution claim.",
    "research_methods": "Choose a method that fits the question, document the procedure, and be transparent about limitations.",
    "responsible_ai": "Add uncertainty, privacy protection, source verification, and escalation for high-impact decisions.",
    "product_strategy": "Define the user, pain point, MVP scope, success metric, and next product iteration.",
    "data_visualization": "Choose charts that match the decision being made and avoid visual designs that exaggerate patterns.",
    "human_ai_interaction": "Study how users understand, trust, misuse, or collaborate with the AI system.",
}


def build_answer(row: pd.Series, model_name: str, profile: dict) -> str:
    category = row["category"]
    risk = row["expected_risk"]
    question = row["question_text"]
    guidance = CATEGORY_GUIDANCE.get(category, "Break the problem into goals, evidence, options, and next steps.")

    if profile["style"] == "balanced":
        risk_sentence = "For high-impact decisions, verify the advice with official sources or a human expert." if risk == "high" else "Keep the scope small and check your progress with evidence."
        return (
            f"{profile['prefix']} For this question — {question} — the best approach is to separate the goal from the next action. "
            f"{guidance} A practical plan is: 1) define the target outcome, 2) list missing information, 3) take one small action this week, "
            f"and 4) review whether the result actually helped. {risk_sentence}"
        )

    if profile["style"] == "concise":
        return (
            f"{profile['prefix']} {guidance} Start with one small task, finish it, and then decide the next step based on what you learned."
        )

    # Intentionally useful but less safe / less nuanced, to make model comparison meaningful.
    return (
        f"{profile['prefix']} For this situation, the optimal move is clear: {guidance} "
        f"Do this immediately and do not spend too much time comparing alternatives."
    )


def main() -> None:
    questions = pd.read_csv(QUESTIONS_PATH)
    rows = []

    for _, row in questions.iterrows():
        for model_name, profile in MODEL_PROFILES.items():
            answer = build_answer(row, model_name, profile)
            rows.append(
                {
                    "question_id": row["question_id"],
                    "model_name": model_name,
                    "answer_text": answer,
                    "answer_length": len(answer.split()),
                }
            )

    answers = pd.DataFrame(rows)
    answers["answer_id"] = answers["question_id"].astype(str) + "__" + answers["model_name"].astype(str)
    answers.to_csv(ANSWERS_PATH, index=False)
    answers.to_csv(SIMULATED_ANSWERS_PATH, index=False)
    print(f"AI answers saved as {ANSWERS_PATH.relative_to(ROOT)}")
    print(f"Simulated answers saved as {SIMULATED_ANSWERS_PATH.relative_to(ROOT)}")
    print("Rows:", answers.shape[0])
    print(answers.head())


if __name__ == "__main__":
    main()
