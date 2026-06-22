from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data"
SIM_PATH = DATA_DIR / "ai_answers.csv"
REAL_PATH = DATA_DIR / "real_ai_answers_imported.csv"
OUT_PATH = DATA_DIR / "ai_answers_combined.csv"


def main() -> None:
    sim = pd.read_csv(SIM_PATH)
    if not REAL_PATH.exists():
        sim.to_csv(OUT_PATH, index=False)
        print("No real imported answers found. Wrote simulated answers only.")
        return
    real = pd.read_csv(REAL_PATH)
    real_min = real[["question_id", "model_name", "answer_text"]].copy()
    real_min["answer_length"] = real_min["answer_text"].fillna("").astype(str).str.split().str.len()
    combined = pd.concat([sim, real_min], ignore_index=True)
    combined = combined.drop_duplicates(subset=["question_id", "model_name"], keep="last")
    combined.to_csv(OUT_PATH, index=False)
    print(f"Combined {len(sim)} simulated + {len(real_min)} real rows -> {OUT_PATH.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
