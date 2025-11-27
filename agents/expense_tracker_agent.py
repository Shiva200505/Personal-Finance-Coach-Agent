import re
from typing import Dict, Tuple
from datetime import datetime

from tools.storage_tool import StorageTool


CATEGORIES = [
    "food", "transport", "entertainment", "shopping", "bills", "healthcare", "other"
]


class ExpenseTrackerAgent:
    """Parses expense statements and stores them with category and timestamp."""

    def __init__(self, storage: StorageTool):
        self.storage = storage

    def parse_expense(self, text: str) -> Tuple[float, str, str]:
        # Extract amount (e.g., "$50", "50", "50.25")
        amt_match = re.search(r"(?:\$\s*)?(\d+(?:\.\d{1,2})?)", text)
        if not amt_match:
            raise ValueError("Could not detect amount. Try 'I spent $50 on groceries'.")
        amount = float(amt_match.group(1))

        # Detect category by keyword mapping
        lower = text.lower()
        category = "other"
        mapping = {
            "food": ["food", "grocer", "restaurant", "dining", "coffee"],
            "transport": ["transport", "uber", "taxi", "bus", "train", "gas", "fuel"],
            "entertainment": ["movie", "cinema", "entertainment", "netflix", "music"],
            "shopping": ["shopping", "clothes", "apparel", "amazon", "purchase"],
            "bills": ["bill", "utilities", "electric", "water", "internet", "phone"],
            "healthcare": ["doctor", "hospital", "pharmacy", "medicine", "health"],
        }
        for cat, keys in mapping.items():
            if any(k in lower for k in keys):
                category = cat
                break

        description = text.strip()
        return amount, category, description

    def add_expense(self, text: str) -> Dict[str, str]:
        amount, category, description = self.parse_expense(text)
        record = self.storage.save_expense(amount, category, description, ts=datetime.utcnow().isoformat())
        return {
            "message": f"Saved: ${record['amount']:.2f} to {record['category']} — {record['description']}",
            "category": record["category"],
        }