import json
from datetime import datetime
from pathlib import Path
from typing import List, Dict

from textblob import TextBlob

from git import Repo

REPORT_DIR = Path("reports")


class ReportWriter:
    """Generate aggregated JSON prediction reports."""

    def __init__(self):
        REPORT_DIR.mkdir(exist_ok=True)
        self.repo = Repo(Path(__file__).resolve().parent)

    def write(self, results: List[Dict], commit: bool = True) -> Path:
        date_str = datetime.utcnow().strftime("%Y-%m-%d")
        filename = REPORT_DIR / f"stock_report_{date_str}.json"
        payload = {
            "date": date_str,
            "results": results,
        }
        filename.write_text(json.dumps(payload, indent=2))
        if commit:
            self.repo.git.add(str(filename))
            self.repo.index.commit(f"Add stock report for {date_str}")
        return filename

    def write_summary(self, results: List[Dict], commit: bool = True) -> Path:
        """Generate a human readable text summary for all stocks."""
        date_str = datetime.utcnow().strftime("%Y-%m-%d")
        filename = REPORT_DIR / f"stock_summary_{date_str}.txt"

        def rec_and_turnover(sent: float, conf_val: float, conf_label: str) -> tuple[str, str]:
            if sent <= -0.2 or conf_val < 30:
                rec = "AVOID"
            elif sent >= 0.2 and conf_val >= 60:
                rec = "BUY"
            else:
                rec = "HOLD"

            turnover = "Indeterminate"
            label = conf_label.lower()
            if label == "high":
                turnover = "2-3 days"
            elif label == "medium":
                turnover = "4-7 days"
            elif label == "low":
                turnover = "7-10 days"
            return rec, turnover

        order = {"BUY": 0, "HOLD": 1, "AVOID": 2}

        summary_data = []
        for item in results:
            pred = item.get("prediction", {})
            sentiment = float(pred.get("score", 0.0))
            conf = pred.get("confidence", {})
            conf_val = float(conf.get("value", 0.0))
            conf_label = str(conf.get("label", ""))
            rec, turnover = rec_and_turnover(sentiment, conf_val, conf_label)
            company = item.get("company", "")
            headlines = item.get("headlines", [])[:2]
            summary_data.append(
                {
                    "symbol": item.get("symbol", ""),
                    "company": company,
                    "sentiment": sentiment,
                    "confidence_value": conf_val,
                    "confidence_label": conf_label,
                    "headlines": headlines,
                    "rec": rec,
                    "turnover": turnover,
                }
            )

        summary_data.sort(key=lambda x: order.get(x["rec"], 3))

        lines: List[str] = []
        for entry in summary_data:
            sym_line = f"Symbol: {entry['symbol']}"
            if entry["company"]:
                sym_line += f" ({entry['company']})"
            lines.append("-" * 40)
            lines.append(sym_line)
            lines.append("")
            if entry["headlines"]:
                lines.append("Top Headline:")
                for h in entry["headlines"]:
                    pol = TextBlob(h).sentiment.polarity
                    if pol > 0.05:
                        rationale = "positive sentiment"
                    elif pol < -0.05:
                        rationale = "negative sentiment"
                    else:
                        rationale = "mixed sentiment"
                    lines.append(f"- \"{h}\" → {rationale}")
                lines.append("")

            sent_score = f"{entry['sentiment']:+.2f}"
            conf_str = f"{entry['confidence_value']:.0f}% ({entry['confidence_label']})"
            lines.append(f"Sentiment Score: {sent_score}")
            lines.append(f"Confidence: {conf_str}")
            lines.append("")

            emoji = "📈" if entry["rec"] == "BUY" else "🔻" if entry["rec"] == "AVOID" else "➖"
            lines.append(f"{emoji} Recommendation: {entry['rec']}")
            lines.append(f"💡 Estimated Turnover: {entry['turnover']}")

            if entry["rec"] == "BUY":
                insight = "Positive news flow may drive short-term gains."
            elif entry["rec"] == "AVOID":
                insight = "Negative signals suggest caution in the short term."
            else:
                insight = "Mixed outlook indicates waiting for clarity."

            lines.append(f"Insight: {insight}")
            lines.append("")

        if lines:
            lines.append("-" * 40)

        filename.write_text("\n".join(lines))
        if commit:
            self.repo.git.add(str(filename))
            self.repo.index.commit(f"Add stock summary for {date_str}")
        return filename
