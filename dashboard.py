from pathlib import Path
import json

import pandas as pd
import streamlit as st


st.set_page_config(page_title="AI Study Advice Evaluation Platform", layout="wide")

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
REPORTS_DIR = BASE_DIR / "reports"
FIGURES_DIR = BASE_DIR / "figures"
CONFIG_PATH = BASE_DIR / "config" / "evaluation_mode.json"

SCORE_COLS = ["accuracy", "helpfulness", "clarity", "actionability", "risk_control"]
RISK_WEIGHTS = {
    "low": {"accuracy": 0.25, "helpfulness": 0.25, "clarity": 0.20, "actionability": 0.20, "risk_control": 0.10},
    "medium": {"accuracy": 0.25, "helpfulness": 0.20, "clarity": 0.15, "actionability": 0.20, "risk_control": 0.20},
    "high": {"accuracy": 0.25, "helpfulness": 0.15, "clarity": 0.10, "actionability": 0.20, "risk_control": 0.30},
}


def read_csv(path: Path) -> pd.DataFrame:
    if not path.exists():
        return pd.DataFrame()
    try:
        return pd.read_csv(path)
    except Exception as exc:
        st.warning(f"Could not read {path.name}: {exc}")
        return pd.DataFrame()


def read_md(path: Path) -> str:
    if not path.exists():
        return ""
    return path.read_text(encoding="utf-8")


def load_config() -> dict:
    if not CONFIG_PATH.exists():
        return {"mode": "simulated"}
    try:
        return json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {"mode": "simulated"}


def weighted_score(row: pd.Series) -> float:
    risk = str(row.get("expected_risk", "medium")).lower()
    weights = RISK_WEIGHTS.get(risk, RISK_WEIGHTS["medium"])
    total = 0
    for col, weight in weights.items():
        total += float(row.get(col, 0) or 0) * weight
    return round(total, 2)


@st.cache_data
def load_ratings() -> pd.DataFrame:
    df = read_csv(DATA_DIR / "ratings.csv")
    if df.empty:
        return df
    for col in SCORE_COLS + ["overall_score"]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")
    if "expected_risk" not in df.columns and "risk_level" in df.columns:
        df["expected_risk"] = df["risk_level"]
    if "question_text" not in df.columns and "student_question" in df.columns:
        df["question_text"] = df["student_question"]
    if "weighted_score" not in df.columns and all(col in df.columns for col in SCORE_COLS):
        df["weighted_score"] = df.apply(weighted_score, axis=1)
    if "needs_review" not in df.columns:
        df["needs_review"] = df.get("overall_score", pd.Series(dtype=float)) < 4
    if "review_priority" not in df.columns:
        df["review_priority"] = "none"
    if "error_type" not in df.columns and "failure_type" in df.columns:
        df["error_type"] = df["failure_type"]
    if "answer_id" not in df.columns and {"question_id", "model_name"}.issubset(df.columns):
        df["answer_id"] = df["question_id"].astype(str) + "__" + df["model_name"].astype(str)
    return df


def metric_row(df: pd.DataFrame, config: dict) -> None:
    total_questions = df["question_id"].nunique() if "question_id" in df else 0
    total_answers = len(df)
    avg = df["overall_score"].mean() if "overall_score" in df else 0
    weighted = df["weighted_score"].mean() if "weighted_score" in df else 0
    review_rate = df["needs_review"].mean() if "needs_review" in df else 0
    p0 = int((df["review_priority"] == "P0").sum()) if "review_priority" in df else 0
    c1, c2, c3, c4, c5, c6 = st.columns(6)
    c1.metric("Questions", total_questions)
    c2.metric("Evaluated Answers", total_answers)
    c3.metric("Mode", config.get("mode", "simulated"))
    c4.metric("Avg Overall", f"{avg:.2f}")
    c5.metric("Risk-Weighted", f"{weighted:.2f}")
    c6.metric("P0 Count", p0)
    st.caption(f"Review rate: {review_rate:.1%}")


def show_report(path: Path, empty_message: str) -> None:
    text = read_md(path)
    if text:
        st.markdown(text)
    else:
        st.info(empty_message)


def model_leaderboard(df: pd.DataFrame) -> pd.DataFrame:
    if df.empty:
        return df
    summary = df.groupby("model_name").agg(
        evaluated_answers=("question_id", "count"),
        overall_score=("overall_score", "mean"),
        risk_weighted_score=("weighted_score", "mean"),
        review_rate=("needs_review", "mean"),
        p0_rate=("review_priority", lambda s: (s == "P0").mean()),
    ).reset_index()
    high = df[df["expected_risk"].eq("high")].groupby("model_name")["weighted_score"].mean().reset_index(name="high_risk_performance")
    summary = summary.merge(high, on="model_name", how="left")
    summary["release_candidate_label"] = "monitor"
    summary.loc[(summary["risk_weighted_score"] >= 4.2) & (summary["p0_rate"] == 0), "release_candidate_label"] = "candidate"
    summary.loc[summary["p0_rate"] > 0, "release_candidate_label"] = "blocked"
    numeric = summary.select_dtypes(include="number").columns
    summary[numeric] = summary[numeric].round(3)
    return summary.sort_values(["release_candidate_label", "risk_weighted_score"], ascending=[True, False])


config = load_config()
df = load_ratings()

st.title("AI Study Advice Evaluation Platform")
st.caption("A human-centered AI evaluation platform for student-advice systems.")

if df.empty:
    st.warning("No evaluated data found yet. Run `python scripts/run_all.py` to generate the demo pipeline.")
    st.stop()

with st.sidebar:
    st.header("Filters")
    model = st.selectbox("Model", ["All"] + sorted(df["model_name"].dropna().unique().tolist()))
    category = st.selectbox("Category", ["All"] + sorted(df.get("category", pd.Series(dtype=str)).dropna().unique().tolist()))
    risk = st.selectbox("Risk", ["All"] + sorted(df.get("expected_risk", pd.Series(dtype=str)).dropna().unique().tolist()))
    failure = st.selectbox("Failure Type", ["All"] + sorted(df.get("error_type", pd.Series(dtype=str)).dropna().unique().tolist()))

filtered = df.copy()
if model != "All":
    filtered = filtered[filtered["model_name"] == model]
if category != "All":
    filtered = filtered[filtered["category"] == category]
if risk != "All":
    filtered = filtered[filtered["expected_risk"] == risk]
if failure != "All":
    filtered = filtered[filtered["error_type"] == failure]

tabs = st.tabs([
    "Overview",
    "Model Leaderboard",
    "Real Model Evaluation",
    "Human Annotation",
    "Statistical Evidence",
    "Review Queue",
    "Case Review",
    "Launch Readiness",
    "Portfolio",
])

with tabs[0]:
    metric_row(filtered, config)
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Average Scores")
        score_cols = [c for c in SCORE_COLS if c in filtered.columns]
        st.bar_chart(filtered[score_cols].mean() if score_cols else pd.Series(dtype=float))
    with col2:
        st.subheader("Failure Types")
        st.bar_chart(filtered.get("error_type", pd.Series(dtype=str)).value_counts())
    st.subheader("Generated Figures")
    figure_names = [
        "risk_weighted_score_by_model.png",
        "review_rate_by_model.png",
        "failure_type_distribution.png",
        "score_by_category.png",
        "high_risk_performance_by_model.png",
    ]
    cols = st.columns(2)
    for idx, name in enumerate(figure_names):
        path = FIGURES_DIR / name
        if path.exists():
            cols[idx % 2].image(str(path), use_container_width=True)

with tabs[1]:
    st.subheader("Model Ranking")
    leaderboard = model_leaderboard(filtered)
    st.dataframe(leaderboard, use_container_width=True, hide_index=True)
    show_report(REPORTS_DIR / "model_leaderboard.md", "Run `python scripts/build_leaderboard.py` to generate the leaderboard report.")

with tabs[2]:
    if (DATA_DIR / "real_model_answers_clean.csv").exists():
        st.subheader("Real Model Evaluation")
        show_report(REPORTS_DIR / "real_model_comparison_report.md", "Run `python scripts/generate_real_model_comparison_report.py`.")
        real_df = read_csv(DATA_DIR / "real_model_answers_clean.csv")
        st.dataframe(real_df, use_container_width=True, hide_index=True)
    else:
        st.info("Real model data has not been imported yet. Fill `data/real_model_answers_template.csv`, run the importer, then switch config mode to `real`.")
        show_report(REPORTS_DIR / "real_model_data_instructions.md", "Real model data instructions are missing.")

with tabs[3]:
    st.subheader("Annotation Completeness")
    show_report(REPORTS_DIR / "annotation_completeness_report.md", "Run `python scripts/check_annotation_completeness.py`.")
    st.subheader("Reliability")
    rel = read_csv(REPORTS_DIR / "human_reliability_by_dimension.csv")
    if not rel.empty:
        st.dataframe(rel, use_container_width=True, hide_index=True)
        if "mean_abs_disagreement" in rel.columns:
            st.bar_chart(rel.set_index("dimension")["mean_abs_disagreement"])
    bias = read_csv(REPORTS_DIR / "rater_bias_summary.csv")
    if not bias.empty:
        st.subheader("Rater Bias Summary")
        st.dataframe(bias, use_container_width=True, hide_index=True)
    show_report(REPORTS_DIR / "human_reliability_report.md", "Run `python scripts/analyze_human_reliability.py`.")

with tabs[4]:
    st.subheader("Bootstrap Model Differences")
    pairwise = read_csv(REPORTS_DIR / "model_pairwise_differences.csv")
    category_diff = read_csv(REPORTS_DIR / "model_category_differences.csv")
    high_risk_diff = read_csv(REPORTS_DIR / "high_risk_model_differences.csv")
    if not pairwise.empty:
        st.dataframe(pairwise, use_container_width=True, hide_index=True)
    if (FIGURES_DIR / "bootstrap_confidence_intervals.png").exists():
        st.image(str(FIGURES_DIR / "bootstrap_confidence_intervals.png"), use_container_width=True)
    with st.expander("Category-Level Comparisons"):
        st.dataframe(category_diff, use_container_width=True, hide_index=True)
    with st.expander("High-Risk-Only Comparisons"):
        st.dataframe(high_risk_diff, use_container_width=True, hide_index=True)
    show_report(REPORTS_DIR / "statistical_analysis.md", "Run `python scripts/analyze_model_differences.py`.")

with tabs[5]:
    st.subheader("Review Queue")
    queue = read_csv(DATA_DIR / "review_queue.csv")
    if queue.empty:
        st.success("No open review queue items were found.")
    else:
        p = st.multiselect("Priority", sorted(queue["priority"].dropna().unique().tolist()), default=sorted(queue["priority"].dropna().unique().tolist()))
        m = st.multiselect("Queue Model", sorted(queue["model_name"].dropna().unique().tolist()), default=sorted(queue["model_name"].dropna().unique().tolist()))
        ft = st.multiselect("Queue Failure Type", sorted(queue["failure_type"].dropna().unique().tolist()), default=sorted(queue["failure_type"].dropna().unique().tolist()))
        qf = queue[queue["priority"].isin(p) & queue["model_name"].isin(m) & queue["failure_type"].isin(ft)]
        st.dataframe(qf, use_container_width=True, hide_index=True)
        st.download_button("Download review queue CSV", qf.to_csv(index=False).encode("utf-8"), "review_queue.csv", "text/csv")
    show_report(REPORTS_DIR / "review_queue_report.md", "Run `python scripts/build_review_queue.py`.")

with tabs[6]:
    st.subheader("Case Review")
    if filtered.empty:
        st.info("No cases match the filters.")
    else:
        qid = st.selectbox("Question", sorted(filtered["question_id"].dropna().unique().tolist()))
        cases = filtered[filtered["question_id"] == qid].sort_values("model_name")
        st.markdown("### Student Question")
        st.info(str(cases.iloc[0].get("question_text", "")))
        st.dataframe(cases[["answer_id", "model_name", "category", "expected_risk", "overall_score", "weighted_score", "review_priority", "error_type"]], use_container_width=True, hide_index=True)
        for _, row in cases.iterrows():
            with st.expander(f"{row['model_name']} answer"):
                st.write(row.get("answer_text", ""))
                st.write("Reviewer notes:", row.get("notes", ""))

with tabs[7]:
    st.subheader("Launch Readiness")
    show_report(REPORTS_DIR / "launch_readiness_report.md", "Run `python scripts/evaluate_launch_readiness.py`.")
    with st.expander("Risk Register"):
        show_report(REPORTS_DIR / "risk_register.md", "No risk register found.")
    with st.expander("Checklist"):
        show_report(REPORTS_DIR / "launch_checklist.md", "No launch checklist found.")

with tabs[8]:
    st.subheader("Portfolio Summary")
    show_report(REPORTS_DIR / "project_one_pager.md", "Run `python scripts/generate_portfolio_assets.py`.")
    with st.expander("Final Research Report"):
        show_report(REPORTS_DIR / "final_research_report.md", "Run `python scripts/generate_final_research_report.py`.")
    with st.expander("Resume Bullets"):
        show_report(REPORTS_DIR / "resume_bullets.md", "Resume bullets missing.")
    with st.expander("Project Pitch"):
        show_report(REPORTS_DIR / "project_pitch_30_seconds.md", "Pitch missing.")
        show_report(REPORTS_DIR / "project_pitch_2_minutes.md", "")
    with st.expander("GitHub README Section"):
        show_report(REPORTS_DIR / "github_readme_section.md", "README section missing.")

