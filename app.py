from pathlib import Path


exec((Path(__file__).resolve().parent / "dashboard.py").read_text(encoding="utf-8"))
