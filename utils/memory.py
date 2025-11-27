from pathlib import Path
import json
from datetime import datetime
from typing import Any, Dict, List, Optional


class Memory:
    """Simple JSON-based memory for conversation history and preferences."""

    def __init__(self, session_id: str = "default") -> None:
        self.session_id = session_id
        self.project_root = Path(__file__).resolve().parents[1]
        self.data_dir = self.project_root / "data"
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.memory_path = self.data_dir / "memory.json"
        if not self.memory_path.exists():
            self._write({"sessions": {}})

    def _read(self) -> Dict[str, Any]:
        try:
            with self.memory_path.open("r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {"sessions": {}}

    def _write(self, data: Dict[str, Any]) -> None:
        with self.memory_path.open("w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)

    def _ensure_session(self) -> Dict[str, Any]:
        data = self._read()
        sessions = data.setdefault("sessions", {})
        session = sessions.setdefault(self.session_id, {"conversation": [], "preferences": {}})
        self._write(data)
        return session

    def append_conversation(self, role: str, text: str) -> None:
        session = self._ensure_session()
        session["conversation"].append({
            "role": role,
            "text": text,
            "ts": datetime.utcnow().isoformat(),
        })
        data = self._read()
        data["sessions"][self.session_id] = session
        self._write(data)

    def get_conversation(self) -> List[Dict[str, Any]]:
        session = self._ensure_session()
        return session.get("conversation", [])

    def set_preference(self, key: str, value: Any) -> None:
        session = self._ensure_session()
        prefs = session.setdefault("preferences", {})
        prefs[key] = value
        data = self._read()
        data["sessions"][self.session_id] = session
        self._write(data)

    def get_preference(self, key: str, default: Optional[Any] = None) -> Any:
        session = self._ensure_session()
        prefs = session.get("preferences", {})
        return prefs.get(key, default)

    def get_preferences(self) -> Dict[str, Any]:
        session = self._ensure_session()
        return session.get("preferences", {})