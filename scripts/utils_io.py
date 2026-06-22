import json
from pathlib import Path
from typing import Iterable

import pandas as pd

from utils_paths import CONFIG_DIR, DATA_DIR, ROOT


EVALUATION_MODE_PATH = CONFIG_DIR / "evaluation_mode.json"
DEFAULT_EVALUATION_MODE = {
    "mode": "simulated",
    "input_file": "data/simulated_model_answers.csv",
    "output_file": "data/evaluated_answers.csv",
    "allowed_modes": ["simulated", "real", "human_scored"],
}


def load_evaluation_config() -> dict:
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    if not EVALUATION_MODE_PATH.exists():
        EVALUATION_MODE_PATH.write_text(json.dumps(DEFAULT_EVALUATION_MODE, indent=2), encoding="utf-8")
        return DEFAULT_EVALUATION_MODE.copy()

    try:
        config = json.loads(EVALUATION_MODE_PATH.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        print("WARNING: config/evaluation_mode.json is invalid. Falling back to simulated mode.")
        return DEFAULT_EVALUATION_MODE.copy()

    merged = DEFAULT_EVALUATION_MODE.copy()
    merged.update(config)
    if merged.get("mode") not in merged.get("allowed_modes", []):
        print(f"WARNING: Unknown evaluation mode `{merged.get('mode')}`. Falling back to simulated mode.")
        merged = DEFAULT_EVALUATION_MODE.copy()
    return merged


def project_path(path: str | Path) -> Path:
    path = Path(path)
    return path if path.is_absolute() else ROOT / path


def read_csv_optional(path: str | Path, required_columns: Iterable[str] | None = None) -> pd.DataFrame:
    resolved = project_path(path)
    if not resolved.exists():
        return pd.DataFrame(columns=list(required_columns or []))
    df = pd.read_csv(resolved)
    if required_columns:
        for col in required_columns:
            if col not in df.columns:
                df[col] = pd.NA
    return df


def active_answer_input_path() -> Path:
    config = load_evaluation_config()
    mode = config.get("mode", "simulated")
    if mode == "real":
        real_path = DATA_DIR / "real_model_answers_clean.csv"
        if real_path.exists():
            return real_path
        print("WARNING: real mode requested but data/real_model_answers_clean.csv is missing. Using simulated answers.")
        return DATA_DIR / "simulated_model_answers.csv"
    if mode == "human_scored":
        human_path = DATA_DIR / "human_scored_answers.csv"
        if human_path.exists():
            return human_path
        print("WARNING: human_scored mode requested but data/human_scored_answers.csv is missing. Using ratings.csv if available.")
        return DATA_DIR / "ratings.csv"
    return project_path(config.get("input_file", "data/simulated_model_answers.csv"))


def normalize_answer_columns(df: pd.DataFrame) -> pd.DataFrame:
    rename_map = {
        "risk_level": "expected_risk",
        "student_question": "question_text",
        "failure_type": "error_type",
        "usefulness_score": "helpfulness",
        "specificity_score": "clarity",
        "empathy_score": "accuracy",
    }
    out = df.rename(columns={k: v for k, v in rename_map.items() if k in df.columns and v not in df.columns}).copy()
    if "answer_id" not in out.columns and {"question_id", "model_name"}.issubset(out.columns):
        out["answer_id"] = out["question_id"].astype(str) + "__" + out["model_name"].astype(str)
    if "answer_length" not in out.columns and "answer_text" in out.columns:
        out["answer_length"] = out["answer_text"].fillna("").astype(str).str.split().str.len()
    return out

