from typing import Dict, List
from datetime import datetime, timedelta

from tools.storage_tool import StorageTool
from tools.search_tool import SearchTool


class SavingsAdvisorAgent:
    """Generates personalized savings advice using spending patterns and web tips."""

    def __init__(self, storage: StorageTool, search: SearchTool):
        self.storage = storage
        self.search = search

    def advise(self) -> Dict[str, any]:
        # Analyze last 30 days
        end = datetime.utcnow()
        start = end - timedelta(days=30)
        expenses = self.storage.get_expenses(start=start.isoformat(), end=end.isoformat())
        by_cat: Dict[str, float] = {}
        for e in expenses:
            by_cat[e["category"]] = round(by_cat.get(e["category"], 0.0) + float(e["amount"]), 2)

        # Heuristic advice
        tips: List[str] = []
        if by_cat.get("entertainment", 0) > 100:
            tips.append("Reduce entertainment subscriptions or switch to free alternatives.")
        if by_cat.get("food", 0) > 200:
            tips.append("Plan meals and buy groceries in bulk; limit dining out.")
        if by_cat.get("transport", 0) > 150:
            tips.append("Use public transport, carpool, or optimize routes to save on fuel.")
        if not tips:
            tips.append("Track recurring charges and cancel unused subscriptions.")

        # Web search tips
        web = self.search.search_financial_tips()
        web_summaries = [f"{r.get('title')}: {r.get('snippet')} ({r.get('link')})" for r in web][:3]

        return {
            "pattern_summary": by_cat,
            "personalized_tips": tips,
            "web_tips": web_summaries,
        }