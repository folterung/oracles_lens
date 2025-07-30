import os
import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict
import requests
from git import Repo

EVAL_DIR = Path('evaluations')
REPORT_DIR = Path('reports')
HISTORY_LOG = Path('history/prediction_accuracy_log.jsonl')

STOCK_API_URL = 'https://www.alphavantage.co/query'

class Evaluator:
    def __init__(self, stock_api_key: str | None = None):
        self.stock_api_key = stock_api_key or os.getenv("STOCK_API_KEY")
        if not self.stock_api_key:
            raise ValueError("STOCK_API_KEY not set")
        EVAL_DIR.mkdir(exist_ok=True)
        HISTORY_LOG.parent.mkdir(exist_ok=True)
        self.repo = Repo(Path(__file__).resolve().parents[1])

    def _previous_report(self) -> Path:
        reports = sorted(REPORT_DIR.glob("stock_report_*.json"))
        if len(reports) < 2:
            raise FileNotFoundError("Not enough prediction reports")
        return reports[-2]

    def _fetch_actual_direction(self, symbol: str, report_date: datetime) -> str | None:
        params = {
            "function": "TIME_SERIES_DAILY_ADJUSTED",
            "symbol": symbol,
            "apikey": self.stock_api_key,
        }
        try:
            resp = requests.get(STOCK_API_URL, params=params, timeout=10)
            resp.raise_for_status()
            data = resp.json()
        except Exception:
            return None

        series = data.get("Time Series (Daily)", {})
        next_day = (report_date + timedelta(days=1)).strftime("%Y-%m-%d")
        prev_str = report_date.strftime("%Y-%m-%d")
        closing_next = series.get(next_day, {}).get("4. close")
        closing_prev = series.get(prev_str, {}).get("4. close")
        if not closing_next or not closing_prev:
            return None
        try:
            next_val = float(closing_next)
            prev_val = float(closing_prev)
        except ValueError:
            return None
        if next_val > prev_val:
            return "up"
        if next_val < prev_val:
            return "down"
        return "neutral"

    def _append_history(self, record: Dict[str, object]) -> None:
        line = json.dumps(record)
        with open(HISTORY_LOG, "a") as f:
            f.write(line + "\n")

    def evaluate(self, symbols: List[str], commit: bool = True) -> Path:
        report_path = self._previous_report()
        report = json.loads(report_path.read_text())
        report_date = datetime.strptime(report.get("date"), "%Y-%m-%d")

        evaluations = []
        for symbol in symbols:
            pred = next((r for r in report.get("results", []) if r.get("symbol") == symbol), None)
            if not pred:
                continue
            predicted_direction = pred.get("prediction", {}).get("direction")
            conf = pred.get("prediction", {}).get("confidence", {}).get("value", 0)
            actual_direction = self._fetch_actual_direction(symbol, report_date)
            accuracy = (actual_direction == predicted_direction) if actual_direction else None
            record = {
                "date": report.get("date"),
                "symbol": symbol,
                "predicted_direction": predicted_direction,
                "actual_direction": actual_direction or "unknown",
                "confidence": round(conf),
                "accuracy": accuracy,
            }
            self._append_history(record)
            evaluations.append(record)

        eval_date = datetime.utcnow().strftime("%Y-%m-%d")
        filename = EVAL_DIR / f"evaluation-{eval_date}.md"
        lines = [f"# Evaluation - {eval_date}", f"Report evaluated: {report_path.name}"]
        for ev in evaluations:
            lines.append("")
            lines.append(f"Symbol: {ev['symbol']}")
            lines.append(f"Predicted direction: {ev['predicted_direction']}")
            lines.append(f"Actual direction: {ev['actual_direction']}")
            lines.append(f"Confidence: {ev['confidence']}")
            lines.append(f"Accuracy: {ev['accuracy']}")
        filename.write_text("\n".join(lines))
        if commit:
            self.repo.git.add(str(filename))
            self.repo.git.add(str(HISTORY_LOG))
            self.repo.index.commit(f"Add evaluation report for {eval_date}")
        return filename
