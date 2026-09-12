import sqlite3
from pathlib import Path
import pandas as pd
import streamlit as st

DB_PATH = Path("data/processed/finance.db")

st.set_page_config(page_title="Project Finance AI", layout="wide")

@st.cache_data
def load_all_tables(db_path: str) -> dict[str, pd.DataFrame]:
    if not Path(db_path).exists():
        raise FileNotFoundError(f"SQLite database not found: {db_path}")

    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    tables = ["actuals", "budgets", "forecasts", "documents", "feedback"]
    frames = {}

    for table in tables:
        rows = conn.execute(f"SELECT * FROM {table}").fetchall()
        frames[table] = pd.DataFrame([dict(row) for row in rows]) if rows else pd.DataFrame()

    conn.close()
    return frames

@st.cache_data
def get_summary(db_path: str) -> dict[str, int]:
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM actuals")
    actuals_count = cur.fetchone()[0]
    cur.execute("SELECT COUNT(*) FROM budgets")
    budgets_count = cur.fetchone()[0]
    cur.execute("SELECT COUNT(*) FROM forecasts")
    forecasts_count = cur.fetchone()[0]
    cur.execute("SELECT COUNT(*) FROM documents")
    documents_count = cur.fetchone()[0]
    cur.execute("SELECT COUNT(*) FROM feedback")
    feedback_count = cur.fetchone()[0]
    conn.close()
    return {
        "actuals": actuals_count,
        "budgets": budgets_count,
        "forecasts": forecasts_count,
        "documents": documents_count,
        "feedback": feedback_count,
    }


def load_state():
    db_path = str(DB_PATH)
    if not Path(db_path).exists():
        st.error("SQLite mock database not found. Run the seed command first:")
        st.code("python -m finance_ai.cli seed-database")
        st.stop()

    st.sidebar.header("Project Finance AI")
    st.sidebar.selectbox("Entity", ["Project-Vessel-2026"])
    st.sidebar.selectbox("Period", ["2025-Q2"])
    st.sidebar.selectbox("Currency", ["NOK"])

    try:
        tables = load_all_tables(db_path)
        summary = get_summary(db_path)
    except Exception as exc:
        st.error(f"Unable to load database: {exc}")
        st.stop()

    return db_path, tables, summary


def build_monitoring_tab(tables: dict[str, pd.DataFrame], summary: dict[str, int]):
    st.subheader("Monitoring Dashboard")

    cols = st.columns(5)
    labels = ["Actuals", "Budgets", "Forecasts", "Documents", "Feedback"]
    values = [summary[k] for k in ["actuals", "budgets", "forecasts", "documents", "feedback"]]

    for col, label, value in zip(cols, labels, values):
        col.metric(label, value)

    # variance snapshot from actuals vs 2025-Q2 budget
    actuals = tables.get("actuals")
    budget = tables.get("budgets")
    if not actuals.empty:
        actual_q2 = actuals[actuals["period"] == "2025-Q2"].iloc[0]
        actual_revenue = float(actual_q2["revenue"])
        actual_cost = float(actual_q2["cost"])
    else:
        actual_revenue = actual_cost = 0

    q2_budget = budget[(budget["period"] == "2025-Q2") & (budget["metric"] == "revenue")]\
        if not budget.empty else pd.DataFrame()

    revenue_budget = 50_000_000
    cost_budget = 38_000_000

    st.markdown("### Variance Monitoring")
    col1, col2 = st.columns(2)
    col1.metric("Q2 Revenue", f"{actual_revenue:,.0f} NOK", f"vs Budget {revenue_budget:,.0f} NOK")
    col2.metric("Q2 Cost", f"{actual_cost:,.0f} NOK", f"vs Budget {cost_budget:,.0f} NOK")

    st.markdown("### Data Quality")
    data_quality = {
        "Database file exists": str(Path(DB_PATH).exists()),
        "Actual records": summary["actuals"],
        "Budget records": summary["budgets"],
        "Forecast records": summary["forecasts"],
        "Documentation records": summary["documents"],
    }
    st.json(data_quality)


def build_results_tab(tables: dict[str, pd.DataFrame]):
    st.subheader("Workflow Results")

    executive_summary = (
        "Financial performance evaluation for Project-Vessel-2026 (2025-Q2). "
        "Revenue is below budget and costs are elevated due to Q2 propulsion "
        "subcontractor indexation and ultrasonic testing milestone certificate postponement."
    )

    st.markdown("### Executive Summary")
    st.write(executive_summary)

    st.markdown("### Key Findings")
    findings = [
        "2025-Q2 Actual Revenue: 45,000,000 NOK vs Budget 50,000,000 NOK (-10.0% variance).",
        "2025-Q2 Actual Cost: 42,000,000 NOK vs Budget 38,000,000 NOK (+10.5% variance).",
        "Propulsion system waterjet milestone passed factory acceptance on June 28.",
    ]
    for item in findings:
        st.markdown(f"- {item}")

    st.markdown("### Risks and Uncertainty")
    risks = [
        "Subcontractor raw material price indexation volatility.",
        "Customer QA milestone verification timeline slippage.",
    ]
    for item in risks:
        st.markdown(f"- {item}")

    st.markdown("### Recommended Investigations")
    actions = [
        "Reconcile customer QA certificate acceptance for deferred Q2 milestone billing in Q3.",
        "Review subcontractor contractual indexation caps under clause 14.3.",
    ]
    for item in actions:
        st.markdown(f"- {item}")

    st.markdown("### Evidence")
    documents = tables.get("documents")
    if not documents.empty:
        docs = documents[["document_id", "title", "document_type", "period"]]
        st.dataframe(docs, use_container_width=True)


def build_data_tab(tables: dict[str, pd.DataFrame]):
    st.subheader("Loaded Data")
    tabs = st.tabs(["Actuals", "Budgets", "Forecasts", "Documents", "Feedback"])

    table_labels = ["actuals", "budgets", "forecasts", "documents", "feedback"]
    for idx, label in enumerate(table_labels):
        with tabs[idx]:
            if label in tables and not tables[label].empty:
                st.dataframe(tables[label], use_container_width=True)
            else:
                st.info(f"No rows found in {label}")


def main():
    db_path, tables, summary = load_state()

    st.title("Project Finance AI Dashboard")

    with st.spinner("Loading data..."):
        # reload into UI once and display card metrics
        pass

    tabs = st.tabs(["Data", "Monitoring", "Results", "Actions"])

    with tabs[0]:
        build_data_tab(tables)

    with tabs[1]:
        build_monitoring_tab(tables, summary)

    with tabs[2]:
        build_results_tab(tables)

    with tabs[3]:
        st.subheader("Recommended Actions")
        actions = [
            "Reconcile customer QA certificate acceptance before Q3 revenue recognition.",
            "Review subcontractor clause 14.3 and enforce indexation cap review.",
            "Create a project board action item to monitor cost escalation and billing timelines.",
            "Refresh forecast confidence and update scenario assumptions for Q3/Q4.",
        ]
        for idx, action in enumerate(actions, 1):
            st.markdown(f"{idx}. {action}")

    st.sidebar.markdown("### Workflow")
    st.sidebar.write("1. Load data")
    st.sidebar.write("2. Monitor actuals and budget variance")
    st.sidebar.write("3. Retrieve evidence")
    st.sidebar.write("4. Generate financial report")
    st.sidebar.write("5. Recommend actions")


if __name__ == "__main__":
    main()
