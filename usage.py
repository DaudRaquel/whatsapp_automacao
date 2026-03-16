import json
import os
from datetime import datetime

from config import AUDIT_LOG_FILE, USAGE_LOG_FILE


class UsageTracker:
    def load(self) -> dict:
        if not os.path.exists(USAGE_LOG_FILE):
            return {}
        try:
            with open(USAGE_LOG_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {}

    def save(self, usage: dict) -> None:
        with open(USAGE_LOG_FILE, "w", encoding="utf-8") as f:
            json.dump(usage, f, ensure_ascii=True, indent=2)

    def append_audit(self, record: dict) -> None:
        try:
            with open(AUDIT_LOG_FILE, "a", encoding="utf-8") as f:
                f.write(json.dumps(record, ensure_ascii=True) + "\n")
        except Exception:
            pass

    def today_key(self) -> str:
        return datetime.now().strftime("%Y-%m-%d")

    def get_day_entry(self, usage: dict, today: str) -> dict:
        entry = usage.get(today, {"total": 0, "manha": 0, "noite": 0})
        if isinstance(entry, int):
            entry = {"total": entry, "manha": 0, "noite": 0}
        return entry
