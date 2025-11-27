import os
from pathlib import Path
from datetime import datetime
import sys

import pandas as pd
import streamlit as st
from dotenv import load_dotenv

# Ensure project root is on sys.path so 'agents' and 'tools' are importable
PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from agents.coordinator_agent import CoordinatorAgent
from tools.storage_tool import StorageTool
from agents.goal_monitor_agent import GoalMonitorAgent


PROJECT_ROOT = Path(__file__).resolve().parents[1]


def init_env():
    env_path = PROJECT_ROOT / ".env"
    if env_path.exists():
        load_dotenv(env_path)
    else:
        load_dotenv()


def get_coordinator():
    if "coordinator" not in st.session_state:
        st.session_state["coordinator"] = CoordinatorAgent(session_id="ui")
    return st.session_state["coordinator"]


def get_storage():
    if "storage" not in st.session_state:
        st.session_state["storage"] = StorageTool()
    return st.session_state["storage"]


def page_home():
    st.title("Personal Finance Coach Agent")
    st.write("Track expenses, analyze budgets, get savings advice, set goals, and generate reports.")
    with st.expander("Quick Start"):
        st.markdown("""
        - Add an expense in 'Add Expense' page.
        - Review 'Budget' for monthly analysis and set budget.
        - Get 'Advice' for savings tips (web-integrated).
        - Use 'Goals' to set and monitor your targets.
        - Export monthly 'Report' as CSV.
        """)
    st.info("Gemini and Serper integrations activate automatically if API keys are set in .env.")


def page_add_expense(coordinator: CoordinatorAgent):
    st.header("Add Expense")
    col1, col2 = st.columns(2)
    with col1:
        amount = st.number_input("Amount (USD)", min_value=0.0, step=1.0)
        category = st.selectbox(
            "Category",
            ["food", "transport", "entertainment", "shopping", "bills", "healthcare", "other"], index=0
        )
    with col2:
        description = st.text_input("Description", "e.g., groceries at local market")

    if st.button("Save Expense"):
        if amount <= 0:
            st.error("Please enter a positive amount.")
        else:
            text = f"I spent ${amount:.2f} on {category} - {description}"
            resp = coordinator.handle(text, explicit_command="expense")
            st.success(resp.get("response", "Saved."))


def page_budget(coordinator: CoordinatorAgent, storage: StorageTool):
    st.header("Budget Analysis")
    current_budget = storage.get_budget_monthly()
    st.write(f"Current monthly budget: ${current_budget:.2f}")
    new_budget = st.number_input("Set monthly budget (USD)", value=float(current_budget), step=10.0)
    if st.button("Update Budget"):
        storage.set_budget_monthly(new_budget)
        st.success(f"Budget updated to ${new_budget:.2f}")

    resp = coordinator.handle("Analyze my budget", explicit_command="budget")
    st.subheader("Analysis")
    st.text(resp.get("response", "No analysis available."))

    # Chart: current month totals by category
    now = datetime.now()
    totals = storage.totals_by_category(now.year, now.month)
    if totals:
        df = pd.DataFrame({"category": list(totals.keys()), "amount": list(totals.values())})
        st.subheader("Spending by Category (Current Month)")
        st.bar_chart(df.set_index("category"))
    else:
        st.info("No expenses recorded this month.")


def page_advice(coordinator: CoordinatorAgent):
    st.header("Savings Advice")
    resp = coordinator.handle("How can I save money?", explicit_command="advice")
    text = resp.get("response", "")
    st.text(text)

    # Extract links from web tips block (simple heuristic)
    links = []
    for line in text.splitlines():
        if line.strip().startswith("-") and "http" in line:
            parts = line.split("(")
            if len(parts) > 1 and parts[-1].startswith("http"):
                url = parts[-1].strip(") ")
                links.append(url)
    if links:
        st.subheader("Links")
        for url in links:
            st.markdown(f"- [{url}]({url})")


def page_goals(storage: StorageTool):
    st.header("Goals")
    gm = GoalMonitorAgent(storage)
    st.subheader("Set Goal")
    with st.form("set_goal"):
        name = st.text_input("Goal name", "Car savings")
        amount = st.number_input("Amount (USD)", min_value=0.0, step=100.0)
        deadline = st.text_input("Deadline (YYYY-MM-DD, optional)", "")
        desc = st.text_input("Description", "")
        submitted = st.form_submit_button("Save Goal")
        if submitted:
            dline = deadline.strip() or None
            res = gm.set_goal(name, amount, dline, desc)
            st.success(res.get("message", "Goal saved."))

    st.subheader("List Goals")
    goals = gm.list_goals()["goals"]
    if goals:
        df = pd.DataFrame(goals)
        st.table(df)
    else:
        st.info("No goals yet.")

    st.subheader("Progress")
    target = st.selectbox("Select goal for progress", [g.get("name") for g in goals] if goals else [])
    if target:
        res = gm.progress(target)
        st.write(
            f"Estimated monthly savings: ${res.get('estimated_monthly_savings', 0):.2f}\n\n"
            f"Required monthly savings: ${res.get('required_monthly_savings', 0):.2f}\n\n"
            f"Months left: {res.get('months_left', 'N/A')}\n\n"
            f"Motivation: {res.get('motivation', '')}"
        )


def page_report(storage: StorageTool):
    st.header("Monthly Report")
    now = datetime.now()
    totals = storage.totals_by_category(now.year, now.month)
    df = pd.DataFrame({"Category": list(totals.keys()), "Amount": list(totals.values())})
    if not df.empty:
        st.table(df)
        st.bar_chart(df.set_index("Category"))
        csv = df.to_csv(index=False).encode("utf-8")
        st.download_button("Download CSV", csv, file_name=f"spending_report_{now.strftime('%Y_%m')}.csv", mime="text/csv")
    else:
        st.info("No spending recorded this month.")


def page_settings(coordinator: CoordinatorAgent):
    st.header("Settings")
    st.write("Session ID:")
    sid = st.text_input("Session ID", value="ui")
    if st.button("Apply Session"):
        st.session_state["coordinator"] = CoordinatorAgent(session_id=sid)
        st.success(f"Session switched to '{sid}'.")
    st.write("Environment: keys loaded from .env if present.")


def page_logs():
    st.header("Logs")
    logs_dir = PROJECT_ROOT / "logs"
    files = sorted(logs_dir.glob("finance_agent_*.log"))
    if not files:
        st.info("No logs yet.")
        return
    latest = files[-1]
    st.write(f"Showing: {latest.name}")
    content = latest.read_text(encoding="utf-8")
    st.code(content[-5000:])


def main():
    init_env()
    coordinator = get_coordinator()
    storage = get_storage()

    st.sidebar.title("Finance Coach")
    page = st.sidebar.radio(
        "Navigate",
        ["Home", "Add Expense", "Budget", "Advice", "Goals", "Report", "Settings", "Logs"],
    )

    if page == "Home":
        page_home()
    elif page == "Add Expense":
        page_add_expense(coordinator)
    elif page == "Budget":
        page_budget(coordinator, storage)
    elif page == "Advice":
        page_advice(coordinator)
    elif page == "Goals":
        page_goals(storage)
    elif page == "Report":
        page_report(storage)
    elif page == "Settings":
        page_settings(coordinator)
    elif page == "Logs":
        page_logs()


if __name__ == "__main__":
    main()