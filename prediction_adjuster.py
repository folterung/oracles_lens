import json
from collections import defaultdict
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Any

LOG_PATH = Path('history/prediction_accuracy_log.jsonl')


def analyze(log_path: Path = LOG_PATH, days: int = 7) -> Dict[str, Dict[str, Any]]:
    """Return metrics per symbol for the last `days` days."""
    metrics: Dict[str, Dict[str, Any]] = {}
    if not log_path.exists():
        return metrics

    cutoff = datetime.utcnow().date() - timedelta(days=days - 1)
    entries_by_symbol: defaultdict[str, list[dict]] = defaultdict(list)

    for line in log_path.read_text().splitlines():
        if not line.strip():
            continue
        try:
            record = json.loads(line)
        except json.JSONDecodeError:
            continue
        date_str = record.get("date")
        if not date_str:
            continue
        try:
            d = datetime.strptime(date_str, "%Y-%m-%d").date()
        except ValueError:
            continue
        if d < cutoff:
            continue
        symbol = record.get("symbol")
        if symbol:
            entries_by_symbol[symbol].append(record)

    for symbol, items in entries_by_symbol.items():
        n = len(items)
        if n == 0:
            continue
        accuracies = [1 for i in items if i.get("accuracy") is True]
        evals = [i for i in items if i.get("accuracy") is not None]
        acc_rate = (sum(accuracies) / len(evals)) if evals else None
        avg_conf = sum(float(i.get("confidence", 0)) for i in items) / n

        if acc_rate is None:
            calibration = "No data"
            acc_pct = None
        else:
            acc_pct = acc_rate * 100
            if acc_pct < avg_conf - 5:
                calibration = "Overconfident"
            elif acc_pct > avg_conf + 5:
                calibration = "Underconfident"
            else:
                calibration = "Well-calibrated"

        suggestion = None
        high_buy = [i for i in items if i.get("predicted_direction") == "up" and float(i.get("confidence", 0)) >= 60]
        if high_buy:
            high_acc = sum(1 for h in high_buy if h.get("accuracy")) / len(high_buy)
            if high_acc < 0.5:
                suggestion = f"{symbol} has {high_acc*100:.0f}% accuracy for high-confidence BUY calls — suggest increasing BUY threshold"
            elif high_acc > 0.75:
                suggestion = f"{symbol} has {high_acc*100:.0f}% accuracy for high-confidence BUY calls — suggest decreasing BUY threshold"

        metrics[symbol] = {
            "accuracy_rate": acc_rate,
            "avg_confidence": avg_conf,
            "calibration": calibration,
            "suggestion": suggestion,
        }

    return metrics


def generate_adjustment_file(log_path: Path = LOG_PATH, days: int = 7) -> tuple[Dict[str, Dict[str, Any]], Path]:
    metrics = analyze(log_path=log_path, days=days)
    date_str = datetime.utcnow().strftime("%Y-%m-%d")
    output_path = Path(f"adjustment_suggestions_{date_str}.txt")
    lines = []
    for symbol, data in metrics.items():
        if data.get("suggestion"):
            lines.append(f"{symbol}: {data['suggestion']}")
    if not lines:
        lines.append("No adjustment suggestions.")
    text = "\n".join(lines)
    output_path.write_text(text)
    print(text)
    return metrics, output_path


if __name__ == "__main__":
    generate_adjustment_file()
