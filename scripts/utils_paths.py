from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data"
REPORTS_DIR = ROOT / "reports"
FIGURES_DIR = ROOT / "figures"
CONFIG_DIR = ROOT / "config"
DOCS_DIR = ROOT / "docs"


def ensure_project_dirs() -> None:
    for path in [DATA_DIR, REPORTS_DIR, FIGURES_DIR, CONFIG_DIR, DOCS_DIR]:
        path.mkdir(parents=True, exist_ok=True)


def rel(path: Path) -> str:
    try:
        return str(path.relative_to(ROOT))
    except ValueError:
        return str(path)

