import os
from pathlib import Path
from typing import Optional

from dotenv import load_dotenv
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from agents.coordinator_agent import CoordinatorAgent
from tools.storage_tool import StorageTool


def welcome(console: Console) -> None:
    console.print(Panel.fit(
        "Personal Finance Coach Agent\n\n"
        "Track expenses, analyze budgets, get savings advice, set goals, and generate reports.\n"
        "Type /help for commands.", title="Welcome", border_style="green"))


def print_help(console: Console, text: Optional[str] = None) -> None:
    console.print(Panel.fit(text or "Type commands or natural language queries.", title="Help", border_style="cyan"))


def cmd_expense(console: Console, coordinator: CoordinatorAgent) -> None:
    console.print("Enter expense in natural language (e.g., 'I spent $50 on groceries'):")
    text = input("> ")
    resp = coordinator.handle(text, explicit_command="expense")
    console.print(Panel.fit(resp["response"], title="Expense Saved", border_style="magenta"))


def cmd_budget(console: Console, coordinator: CoordinatorAgent, storage: StorageTool) -> None:
    console.print("View budget analysis or set monthly budget.")
    console.print("Enter 'set <amount>' to change budget or press Enter to analyze:")
    text = input("> ")
    if text.strip().lower().startswith("set "):
        try:
            amt = float(text.strip().split()[1])
            storage.set_budget_monthly(amt)
            console.print(f"Budget set to ${amt:.2f}")
        except Exception:
            console.print("Invalid amount.")
    else:
        resp = coordinator.handle("Analyze my budget", explicit_command="budget")
        console.print(Panel.fit(resp["response"], title="Budget Analysis", border_style="yellow"))


def cmd_advice(console: Console, coordinator: CoordinatorAgent) -> None:
    resp = coordinator.handle("How can I save money?", explicit_command="advice")
    console.print(Panel.fit(resp["response"], title="Savings Advice", border_style="blue"))


def cmd_goal(console: Console, coordinator: CoordinatorAgent, storage: StorageTool) -> None:
    console.print("Goal options: set, list, progress")
    choice = input("Choose [set/list/progress]: ").strip().lower()
    from agents.goal_monitor_agent import GoalMonitorAgent
    goal_agent = GoalMonitorAgent(storage)

    if choice == "set":
        name = input("Goal name: ")
        amount = float(input("Amount to save (USD): "))
        deadline = input("Deadline (YYYY-MM-DD, optional): ").strip() or None
        desc = input("Description: ")
        res = goal_agent.set_goal(name, amount, deadline, desc)
        print(res["message"])
    elif choice == "list":
        res = goal_agent.list_goals()
        table = Table(title="Goals")
        table.add_column("Name")
        table.add_column("Amount")
        table.add_column("Deadline")
        table.add_column("Description")
        for g in res["goals"]:
            table.add_row(str(g.get("name")), f"${float(g.get('amount')):.2f}", str(g.get("deadline")), str(g.get("description")))
        console.print(table)
    elif choice == "progress":
        name = input("Goal name (optional): ").strip() or None
        res = goal_agent.progress(name)
        console.print(Panel.fit(
            f"Estimated monthly savings: ${res.get('estimated_monthly_savings', 0):.2f}\n"
            f"Required monthly savings: ${res.get('required_monthly_savings', 0):.2f}\n"
            f"Months left: {res.get('months_left', 'N/A')}\n"
            f"Motivation: {res.get('motivation', '')}",
            title="Goal Progress", border_style="green"))
    else:
        console.print("Unknown choice.")


def cmd_report(console: Console, coordinator: CoordinatorAgent) -> None:
    resp = coordinator.handle("Show my spending report", explicit_command="report")
    console.print(Panel.fit(resp["response"], title="Spending Report", border_style="white"))


def main() -> None:
    # Load env keys from .env if available
    env_path = Path(__file__).resolve().parent / ".env"
    if env_path.exists():
        load_dotenv(env_path)
    else:
        load_dotenv()

    console = Console()
    welcome(console)

    coordinator = CoordinatorAgent(session_id="local")
    storage = StorageTool()

    while True:
        try:
            text = input("\nCommand or message (/help for options): ").strip()
        except (EOFError, KeyboardInterrupt):
            console.print("\nGoodbye!")
            break

        if not text:
            continue

        if text.lower() in {"/quit", "quit", ":q"}:
            console.print("Goodbye!")
            break
        elif text.lower() in {"/help", "help"}:
            print_help(console, coordinator._help_text())
        elif text.lower().startswith("/expense"):
            cmd_expense(console, coordinator)
        elif text.lower().startswith("/budget"):
            cmd_budget(console, coordinator, storage)
        elif text.lower().startswith("/advice"):
            cmd_advice(console, coordinator)
        elif text.lower().startswith("/goal"):
            cmd_goal(console, coordinator, storage)
        elif text.lower().startswith("/report"):
            cmd_report(console, coordinator)
        else:
            # Free-form handling via coordinator intent detection
            resp = coordinator.handle(text)
            console.print(Panel.fit(resp["response"], title="Agent", border_style="cyan"))


if __name__ == "__main__":
    main()