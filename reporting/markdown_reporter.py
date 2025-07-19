import os
from datetime import datetime
from pathlib import Path
from git import Repo

from .mermaid_utils import flowchart

REPORT_DIR = Path('reports')

class MarkdownReporter:
    def __init__(self):
        REPORT_DIR.mkdir(exist_ok=True)
        self.repo = Repo(Path(__file__).resolve().parents[1])

    def generate_report(self, news_items, insights, prediction, symbol: str) -> Path:
        date_str = datetime.utcnow().strftime('%Y-%m-%d')
        filename = REPORT_DIR / f'prediction-{date_str}.md'
        nodes = {'A': 'Fetch News', 'B': 'Analyze Sentiment', 'C': 'Predict Stock'}
        edges = [('A', 'B'), ('B', 'C')]
        diagram = flowchart(nodes, edges)
        lines = [f"# Stock Prediction Report - {date_str}", f"**Symbol:** {symbol}", '', '## News Headlines']
        for item in news_items:
            lines.append(f"- {item.get('title')}")

        # Filter insights relevant to symbol
        symbol_upper = symbol.upper()
        relevant: list[dict] = []
        for ins in insights:
            entities = [str(e).upper() for e in ins.get('affected_entities', [])]
            if symbol_upper in entities:
                relevant.append(ins)

        lines.append('')
        lines.append(f'## Relevant Insights for {symbol_upper}')
        if not relevant:
            lines.append('No direct references to this symbol found.')
        else:
            for ins in relevant:
                sentiment = float(ins.get('sentiment', 0.0))
                conf = float(ins.get('confidence_score', 0.0))
                duration = ins.get('impact_duration', '')
                rationale = ins.get('rationale', '')
                precedent = ins.get('precedent')
                lines.append(f"- Sentiment: {sentiment:+.2f} | Confidence: {conf:.1f}% | Duration: {duration}")
                if rationale:
                    lines.append(f"  - Rationale: {rationale}")
                if precedent:
                    lines.append(f"  - Precedent: {precedent}")

        lines.append('')
        lines.append(f'Matching insights: {len(relevant)}')
        avg_conf = 0.0
        if relevant:
            avg_conf = sum(float(i.get('confidence_score', 0.0)) for i in relevant) / len(relevant)

        direction_sign = '+' if prediction > 0.05 else '-' if prediction < -0.05 else '0'

        lines.append('')
        lines.append('## Prediction')
        lines.append(f"Predicted movement score: {prediction:+.2f}")
        lines.append(f"Final predicted direction: {direction_sign}")
        lines.append(f"Average confidence: {avg_conf:.1f}%")
        lines.append('')
        lines.append('## Process Diagram')
        lines.append(diagram)
        filename.write_text('\n'.join(lines))
        self.repo.git.add(str(filename))
        self.repo.index.commit(f"Add prediction report for {date_str}")
        return filename
