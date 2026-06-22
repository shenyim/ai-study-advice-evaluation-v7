from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data"
TEMPLATE_PATH = DATA_DIR / "ratings_template.csv"
RATINGS_PATH = DATA_DIR / "ratings.csv"

SCORE_COLS = ["accuracy", "helpfulness", "clarity", "actionability", "risk_control"]

MODEL_BASE = {
    "Balanced_GPT": {"accuracy": 4.7, "helpfulness": 4.6, "clarity": 4.6, "actionability": 4.5, "risk_control": 4.7},
    "Concise_Model": {"accuracy": 4.2, "helpfulness": 3.8, "clarity": 4.4, "actionability": 3.5, "risk_control": 3.9},
    "Overconfident_Model": {"accuracy": 3.8, "helpfulness": 3.7, "clarity": 4.1, "actionability": 3.8, "risk_control": 2.9},
}

DEFAULT_MODEL_BASE = {"accuracy": 4.1, "helpfulness": 4.0, "clarity": 4.0, "actionability": 3.9, "risk_control": 4.0}

RISK_ADJUSTMENTS = {
    "low": {"risk_control": 0.2, "actionability": 0.1},
    "medium": {},
    "high": {"risk_control": -0.4, "actionability": -0.2, "accuracy": -0.1},
}

DIFFICULTY_ADJUSTMENTS = {
    "easy": {"accuracy": 0.1, "clarity": 0.1},
    "medium": {},
    "hard": {"accuracy": -0.2, "helpfulness": -0.2, "actionability": -0.2},
}

CATEGORY_ADJUSTMENTS = {
    "phd_planning": {"risk_control": -0.1, "actionability": -0.1},
    "career_planning": {"risk_control": -0.1},
    "responsible_ai": {"risk_control": -0.1},
    "ai_evaluation": {"accuracy": 0.1, "helpfulness": 0.1},
    "programming": {"actionability": 0.2},
    "data_science": {"actionability": 0.1},
}

ERROR_RULES = [
    ("risk_control", 3.5, "overconfident"),
    ("actionability", 3.8, "missing_steps"),
    ("helpfulness", 3.8, "generic_advice"),
    ("accuracy", 3.8, "possible_inaccuracy"),
]


def clamp(score: float) -> float:
    return round(max(1.0, min(5.0, score)), 1)


def deterministic_noise(question_id: str, model_name: str, col: str) -> float:
    seed = sum(ord(c) for c in f"{question_id}-{model_name}-{col}")
    return ((seed % 5) - 2) * 0.05


def score_row(row: pd.Series) -> dict:
    scores = MODEL_BASE.get(row["model_name"], DEFAULT_MODEL_BASE).copy()
    for adjustments in [RISK_ADJUSTMENTS.get(row["expected_risk"], {}), DIFFICULTY_ADJUSTMENTS.get(row["difficulty"], {}), CATEGORY_ADJUSTMENTS.get(row["category"], {})]:
        for col, delta in adjustments.items():
            scores[col] += delta

    for col in SCORE_COLS:
        scores[col] = clamp(scores[col] + deterministic_noise(row["question_id"], row["model_name"], col))

    # Balanced model intentionally gets stronger high-risk control to represent a safer tuned model.
    if row["model_name"] == "Balanced_GPT" and row["expected_risk"] == "high":
        scores["risk_control"] = max(scores["risk_control"], 4.5)

    error_type = "none"
    for col, threshold, label in ERROR_RULES:
        if scores[col] < threshold:
            error_type = label
            break

    notes = build_notes(row, scores, error_type)
    scores["overall_score"] = round(sum(scores[col] for col in SCORE_COLS) / len(SCORE_COLS), 2)
    scores["error_type"] = error_type
    scores["notes"] = notes
    return scores


def build_notes(row: pd.Series, scores: dict, error_type: str) -> str:
    model = row["model_name"]
    risk = row["expected_risk"]
    if error_type == "none":
        return f"{model} gives a usable answer with acceptable clarity and guardrails for a {risk}-risk question."
    if error_type == "overconfident":
        return f"{model} needs stronger uncertainty language, official-source verification, and escalation for {risk}-risk advice."
    if error_type == "missing_steps":
        return f"{model} is directionally useful but should add concrete steps, examples, or a short checklist."
    if error_type == "generic_advice":
        return f"{model} should personalize the answer more strongly to the student's background and goal."
    return f"{model} should reduce unsupported claims and make the answer easier to verify."


def main() -> None:
    df = pd.read_csv(TEMPLATE_PATH)
    if "accuracy" in df.columns and pd.to_numeric(df["accuracy"], errors="coerce").notna().any():
        print("Ratings template already contains human/provided scores. Preserving them as data/ratings.csv.")
        df.to_csv(RATINGS_PATH, index=False)
        return

    scored_rows = []
    for _, row in df.iterrows():
        scores = score_row(row)
        row_dict = row.to_dict()
        row_dict.update(scores)
        scored_rows.append(row_dict)

    out = pd.DataFrame(scored_rows)
    out.to_csv(RATINGS_PATH, index=False)

    print(f"{RATINGS_PATH.relative_to(ROOT)} created.")
    print("Rows:", len(out))
    print(out.groupby("model_name")["overall_score"].mean().sort_values(ascending=False))


if __name__ == "__main__":
    main()
