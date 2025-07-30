import json
from datetime import datetime
from pathlib import Path
from typing import List, Dict

from git import Repo

REPORT_DIR = Path("reports")


class ReportWriter:
    """Generate aggregated JSON prediction reports."""

    def __init__(self):
        REPORT_DIR.mkdir(exist_ok=True)
        self.repo = Repo(Path(__file__).resolve().parent)

    def write(self, results: List[Dict]) -> Path:
        date_str = datetime.utcnow().strftime("%Y-%m-%d")
        filename = REPORT_DIR / f"stock_report_{date_str}.json"
        payload = {
            "date": date_str,
            "results": results,
        }
        filename.write_text(json.dumps(payload, indent=2))
        self.repo.git.add(str(filename))
        self.repo.index.commit(f"Add stock report for {date_str}")
        return filename
