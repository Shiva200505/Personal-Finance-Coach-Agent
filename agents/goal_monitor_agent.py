from typing import Dict, Any, Optional
from datetime import datetime

from tools.storage_tool import StorageTool


class GoalMonitorAgent:
    """Stores financial goals and tracks saving requirements and progress heuristics."""

    def __init__(self, storage: StorageTool):
        self.storage = storage

    def set_goal(self, name: str, amount: float, deadline: Optional[str], description: str) -> Dict[str, Any]:
        goal = self.storage.save_goal(name, amount, deadline, description)
        return {"message": f"Goal saved: {goal['name']} — ${goal['amount']:.2f}"}

    def list_goals(self) -> Dict[str, Any]:
        goals = self.storage.get_goals()
        return {"goals": goals}

    def progress(self, goal_name: Optional[str] = None) -> Dict[str, Any]:
        # Heuristic: monthly savings = max(budget - monthly spending, 0)
        now = datetime.now()
        totals = self.storage.totals_by_category(now.year, now.month)
        spent = sum(totals.values())
        monthly_budget = self.storage.get_budget_monthly()
        monthly_savings = max(monthly_budget - spent, 0)

        goals = self.storage.get_goals()
        selected = None
        for g in goals:
            if not goal_name or g.get("name") == goal_name:
                selected = g
                break

        if not selected:
            return {"message": "No matching goal found."}

        amount = float(selected.get("amount", 0))
        deadline = selected.get("deadline")
        months_left = None
        if deadline:
            try:
                dl = datetime.fromisoformat(deadline)
                months_left = max((dl.year - now.year) * 12 + (dl.month - now.month), 0)
            except Exception:
                months_left = None

        per_month_required = None
        if months_left and months_left > 0:
            per_month_required = round(amount / months_left, 2)
        else:
            per_month_required = round(amount / 12, 2)  # default to 1 year if no deadline

        motivation = "Stay consistent! Automate a monthly transfer to hit your goal."

        return {
            "goal": selected,
            "estimated_monthly_savings": round(monthly_savings, 2),
            "required_monthly_savings": per_month_required,
            "months_left": months_left,
            "motivation": motivation,
        }