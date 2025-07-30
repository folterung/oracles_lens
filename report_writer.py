from datetime import datetime
from pathlib import Path
from typing import List, Dict, Tuple

from git import Repo

REPORT_DIR = Path("reports")


class ReportWriter:
    """Generate markdown prediction reports."""

    def __init__(self):
        REPORT_DIR.mkdir(exist_ok=True)
        self.repo = Repo(Path(__file__).resolve().parent)

    def write(self, symbol: str, items: List[Dict], weighted_score: float, confidence: Tuple[float, str]) -> Path:
        date_str = datetime.utcnow().strftime("%Y-%m-%d")
        filename = REPORT_DIR / f"{date_str}_{symbol}_report.txt"
        lines = [f"# Stock Prediction Report - {date_str}", f"Symbol: {symbol}", ""]
        lines.append("Top Headlines:")
        top_items = items[:5]
        for it in top_items:
            lines.append(f"- \"{it['title']}\"")
            lines.append(
                f"  → Matched: \"{it['keyword']}\", Relevance: {it['relevance_score']:.2f}, Sentiment: {it['sentiment']:+.2f}"
            )
        lines.append("")
        direction_icon = '📈' if weighted_score > 0 else '📉' if weighted_score < 0 else '➖'
        direction_word = 'Upward' if weighted_score > 0 else 'Downward' if weighted_score < 0 else 'Sideways'
        conf_value = round(confidence[0])
        lines.append(f"Prediction: {weighted_score:+.2f}")
        lines.append(f"Direction: {direction_icon} {direction_word}")
        lines.append(f"Confidence: {conf_value}% ({confidence[1]})")
        filename.write_text("\n".join(lines) + "\n")
        self.repo.git.add(str(filename))
        self.repo.index.commit(f"Add prediction report for {symbol} on {date_str}")
        return filename
