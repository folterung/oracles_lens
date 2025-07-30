import json
import logging
from pathlib import Path
from typing import List, Dict


class WatchlistManager:
    """Load and save watchlist entries from a JSON file."""

    def __init__(self, path: str | Path = "watchlist.json") -> None:
        self.path = Path(path)

    def load(self) -> List[Dict]:
        if not self.path.exists():
            return []
        try:
            data = json.loads(self.path.read_text())
            if isinstance(data, list):
                return data
        except Exception as e:  # pragma: no cover - logging
            logging.exception("Failed to parse watchlist: %s", e)
        return []

    def save(self, entries: List[Dict]) -> None:
        self.path.write_text(json.dumps(entries, indent=2))
