from pathlib import Path

import pandas as pd


def write_markdown(path: Path, lines: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")


def md_table(df: pd.DataFrame, max_rows: int = 30) -> str:
    if df is None or df.empty:
        return "_No rows available._"
    view = df.head(max_rows).copy()
    try:
        return view.to_markdown(index=False)
    except ImportError:
        columns = list(view.columns)
        lines = [
            "| " + " | ".join(str(col) for col in columns) + " |",
            "| " + " | ".join("---" for _ in columns) + " |",
        ]
        for _, row in view.iterrows():
            values = [str(row[col]).replace("\n", " ") for col in columns]
            lines.append("| " + " | ".join(values) + " |")
        return "\n".join(lines)
