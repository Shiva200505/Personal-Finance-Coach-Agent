from typing import Dict, List
from datetime import datetime

from tools.storage_tool import StorageTool

try:
    import google.generativeai as genai
except Exception:
    genai = None


class BudgetAnalyzerAgent:
    """Analyzes spending vs budget and produces natural language summaries."""

    def __init__(self, storage: StorageTool, gemini_model = None):
        self.storage = storage
        self.model = gemini_model

    def analyze_current_month(self) -> Dict[str, str]:
        now = datetime.now()
        year, month = now.year, now.month
        totals = self.storage.totals_by_category(year, month)
        budget = self.storage.get_budget_monthly()
        total_spent = round(sum(totals.values()), 2)
        remaining = round(budget - total_spent, 2)
        status = "OK" if remaining >= 0 else "Over budget"

        summary = {
            "totals": totals,
            "budget": budget,
            "spent": total_spent,
            "remaining": remaining,
            "status": status,
        }

        # Natural language using Gemini if available
        if self.model:
            prompt = (
                "You are a helpful finance assistant. Summarize this monthly budget analysis "
                "clearly with warnings if overspending and 2-3 actionable tips.\n"
                f"Data: {summary}"
            )
            try:
                resp = self.model.generate_content(prompt)
                nl = resp.text.strip() if hasattr(resp, "text") else str(resp)
            except Exception:
                nl = self._fallback_text(summary)
        else:
            nl = self._fallback_text(summary)

        return {
            "analysis": nl,
        }

    def _fallback_text(self, s: Dict[str, any]) -> str:
        lines = [
            f"Budget: ${s['budget']:.2f}",
            f"Spent: ${s['spent']:.2f}",
            f"Remaining: ${s['remaining']:.2f} ({s['status']})",
            "Category totals:",
        ]
        for k, v in s["totals"].items():
            lines.append(f"- {k}: ${v:.2f}")
        if s["remaining"] < 0:
            lines.append("Warning: You're over budget. Consider cutting discretionary spend and reviewing subscriptions.")
        else:
            lines.append("Tip: Automate savings by transferring remaining funds to a savings account.")
        return "\n".join(lines)