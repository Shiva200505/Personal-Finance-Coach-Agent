import os
import requests
from typing import Any, Dict, List


class SearchTool:
    """Serper API integration (Google Search) with graceful fallback."""

    def __init__(self) -> None:
        self.api_key = os.getenv("SERPER_API_KEY")
        self.endpoint = "https://google.serper.dev/search"

    def _search(self, query: str, num: int = 5) -> List[Dict[str, Any]]:
        if not self.api_key:
            # Fallback tips without external API
            return [{
                "title": "General Savings Tips",
                "link": "https://example.com/savings-tips",
                "snippet": "Track spending, set goals, automate transfers, and cut recurring costs.",
            }]
        headers = {"X-API-KEY": self.api_key, "Content-Type": "application/json"}
        payload = {"q": query, "num": num}
        try:
            resp = requests.post(self.endpoint, json=payload, headers=headers, timeout=15)
            resp.raise_for_status()
            data = resp.json()
            results = []
            for item in data.get("organic", [])[:num]:
                results.append({
                    "title": item.get("title"),
                    "link": item.get("link"),
                    "snippet": item.get("snippet"),
                })
            return results or []
        except Exception:
            return []

    def search_financial_tips(self, extra: str = "practical personal savings tips") -> List[Dict[str, Any]]:
        return self._search(extra)

    def search_interest_rates(self) -> List[Dict[str, Any]]:
        return self._search("current savings account interest rates")

    def search_investment_advice(self) -> List[Dict[str, Any]]:
        return self._search("beginner investment advice low-cost index funds")