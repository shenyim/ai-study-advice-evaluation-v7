from pathlib import Path

import pandas as pd

try:
    import matplotlib.pyplot as plt
except ModuleNotFoundError:
    plt = None

ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data"
FIGURES_DIR = ROOT / "figures"
CLEAN_PATH = DATA_DIR / "student_questions_clean.csv"
EDA_PATH = DATA_DIR / "student_questions_eda.csv"


def save_bar(series: pd.Series, title: str, xlabel: str, ylabel: str, path: Path) -> None:
    if plt is None:
        print(f"WARNING: matplotlib unavailable; skipped {path.name}")
        return
    plt.figure()
    series.plot(kind="bar")
    plt.title(title)
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.xticks(rotation=45, ha="right")
    plt.tight_layout()
    plt.savefig(path)
    plt.close()


def main() -> None:
    FIGURES_DIR.mkdir(exist_ok=True)
    df = pd.read_csv(CLEAN_PATH)
    df["question_length"] = df["question_text"].astype(str).str.len()

    print("===== BASIC INFO =====")
    print(df.head())
    print("\nShape:", df.shape)
    print("\n===== CATEGORY DISTRIBUTION =====")
    print(df["category"].value_counts())
    print("\n===== RISK DISTRIBUTION =====")
    print(df["expected_risk"].value_counts())
    print("\n===== CATEGORY x RISK =====")
    print(pd.crosstab(df["category"], df["expected_risk"]))

    save_bar(df["category"].value_counts(), "Question Count by Category", "Category", "Count", FIGURES_DIR / "category_distribution.png")
    save_bar(df["expected_risk"].value_counts(), "Question Count by Expected Risk", "Expected Risk", "Count", FIGURES_DIR / "risk_distribution.png")

    df.to_csv(EDA_PATH, index=False)
    print(f"\nEDA file saved as {EDA_PATH.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
