from pathlib import Path
import json
from typing import Any, Dict, List, Optional, Tuple
from datetime import datetime


class StorageTool:
    """JSON file storage for expenses, goals, and preferences."""

    def __init__(self) -> None:
        self.project_root = Path(__file__).resolve().parents[1]
        self.data_dir = self.project_root / "data"
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.path = self.data_dir / "simple_storage.json"
        if not self.path.exists():
            self._write({
                "expenses": [],
                "goals": [],
                "preferences": {"budget_monthly": 1000},
            })

    def _read(self) -> Dict[str, Any]:
        try:
            with self.path.open("r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {"expenses": [], "goals": [], "preferences": {"budget_monthly": 1000}}

    def _write(self, data: Dict[str, Any]) -> None:
        with self.path.open("w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)

    # Expenses
    def save_expense(self, amount: float, category: str, description: str, ts: Optional[str] = None) -> Dict[str, Any]:
        data = self._read()
        record = {
            "amount": round(float(amount), 2),
            "category": category,
            "description": description,
            "timestamp": ts or datetime.utcnow().isoformat(),
        }
        data["expenses"].append(record)
        self._write(data)
        return record

    def get_expenses(self, start: Optional[str] = None, end: Optional[str] = None, category: Optional[str] = None) -> List[Dict[str, Any]]:
        data = self._read()
        expenses = data.get("expenses", [])
        def in_range(e: Dict[str, Any]) -> bool:
            ts = datetime.fromisoformat(e["timestamp"]) if isinstance(e["timestamp"], str) else e["timestamp"]
            ok_start = True if not start else ts >= datetime.fromisoformat(start)
            ok_end = True if not end else ts <= datetime.fromisoformat(end)
            ok_cat = True if not category else e.get("category") == category
            return ok_start and ok_end and ok_cat
        return [e for e in expenses if in_range(e)]

    def totals_by_category(self, year: int, month: int) -> Dict[str, float]:
        data = self._read()
        totals: Dict[str, float] = {}
        for e in data.get("expenses", []):
            ts = datetime.fromisoformat(e["timestamp"]) if isinstance(e["timestamp"], str) else e["timestamp"]
            if ts.year == year and ts.month == month:
                cat = e.get("category", "other")
                totals[cat] = round(totals.get(cat, 0.0) + float(e.get("amount", 0.0)), 2)
        return totals

    # Goals
    def save_goal(self, name: str, amount: float, deadline: Optional[str], description: str) -> Dict[str, Any]:
        data = self._read()
        goal = {
            "name": name,
            "amount": round(float(amount), 2),
            "deadline": deadline,
            "description": description,
            "created": datetime.utcnow().isoformat(),
        }
        data["goals"].append(goal)
        self._write(data)
        return goal

    def get_goals(self) -> List[Dict[str, Any]]:
        data = self._read()
        return data.get("goals", [])

    # Preferences
    def set_budget_monthly(self, amount: float) -> None:
        data = self._read()
        prefs = data.setdefault("preferences", {})
        prefs["budget_monthly"] = round(float(amount), 2)
        self._write(data)

    def get_budget_monthly(self) -> float:
        data = self._read()
        prefs = data.get("preferences", {})
        return float(prefs.get("budget_monthly", 1000))