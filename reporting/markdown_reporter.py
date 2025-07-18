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

    def generate_report(self, news_items, sentiments, prediction) -> Path:
        date_str = datetime.utcnow().strftime('%Y-%m-%d')
        filename = REPORT_DIR / f'prediction-{date_str}.md'
        nodes = {'A': 'Fetch News', 'B': 'Analyze Sentiment', 'C': 'Predict Stock'}
        edges = [('A', 'B'), ('B', 'C')]
        diagram = flowchart(nodes, edges)
        lines = [f"# Stock Prediction Report - {date_str}", '', '## News Headlines']
        for item, sentiment in zip(news_items, sentiments):
            lines.append(f"- {item.get('title')} (sentiment: {sentiment:+.2f})")
        lines.append('')
        lines.append('## Prediction')
        lines.append(f"Predicted movement score: {prediction:+.2f}")
        lines.append('')
        lines.append('## Process Diagram')
        lines.append(diagram)
        filename.write_text('\n'.join(lines))
        self.repo.git.add(str(filename))
        self.repo.index.commit(f"Add prediction report for {date_str}")
        return filename
