from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data"
RAW_PATH = DATA_DIR / "student_questions_raw.csv"
CLEAN_PATH = DATA_DIR / "student_questions_clean.csv"


def main() -> None:
    df = pd.read_csv(RAW_PATH)

    print("===== BEFORE CLEANING =====")
    print(df)
    print("\nShape:", df.shape)
    print("\nMissing values:")
    print(df.isna().sum())

    df = df.drop_duplicates(subset=["question_id"], keep="first")

    text_columns = ["question_id", "question_text", "category", "difficulty", "expected_risk"]
    for col in text_columns:
        df[col] = df[col].astype(str).str.strip()

    df["category"] = df["category"].str.lower()
    df["difficulty"] = df["difficulty"].str.lower()
    df["expected_risk"] = df["expected_risk"].str.lower()

    df["student_background"] = df["student_background"].fillna("unknown")
    df["student_background"] = df["student_background"].astype(str).str.strip().str.lower()

    df["difficulty"] = df["difficulty"].replace({"medum": "medium"})

    valid_difficulty = ["easy", "medium", "hard"]
    df.loc[~df["difficulty"].isin(valid_difficulty), "difficulty"] = "unknown"

    valid_risk = ["low", "medium", "high"]
    df.loc[~df["expected_risk"].isin(valid_risk), "expected_risk"] = "unknown"

    print("\n===== AFTER CLEANING =====")
    print(df)
    print("\nShape:", df.shape)
    print("\nMissing values:")
    print(df.isna().sum())
    print("\nCategory counts:")
    print(df["category"].value_counts())
    print("\nDifficulty counts:")
    print(df["difficulty"].value_counts())
    print("\nRisk counts:")
    print(df["expected_risk"].value_counts())

    df.to_csv(CLEAN_PATH, index=False)
    print(f"\nCleaned file saved as {CLEAN_PATH.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
