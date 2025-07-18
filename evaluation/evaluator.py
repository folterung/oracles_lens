import os
from datetime import datetime, timedelta
from pathlib import Path
import requests
from git import Repo

EVAL_DIR = Path('evaluations')
REPORT_DIR = Path('reports')

STOCK_API_URL = 'https://www.alphavantage.co/query'

class Evaluator:
    def __init__(self, stock_api_key: str = None):
        self.stock_api_key = stock_api_key or os.getenv('STOCK_API_KEY')
        if not self.stock_api_key:
            raise ValueError('STOCK_API_KEY not set')
        EVAL_DIR.mkdir(exist_ok=True)
        self.repo = Repo(Path(__file__).resolve().parents[1])

    def _latest_report(self) -> Path:
        reports = sorted(REPORT_DIR.glob('prediction-*.md'))
        if not reports:
            raise FileNotFoundError('No prediction reports found')
        return reports[-1]

    def evaluate(self, symbol: str):
        report_path = self._latest_report()
        date_str = report_path.stem.split('-')[-1]
        report_date = datetime.strptime(date_str, '%Y-%m-%d')
        # fetch actual close price for next day using AlphaVantage
        params = {
            'function': 'TIME_SERIES_DAILY_ADJUSTED',
            'symbol': symbol,
            'apikey': self.stock_api_key,
        }
        response = requests.get(STOCK_API_URL, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        series = data.get('Time Series (Daily)', {})
        next_day = (report_date + timedelta(days=1)).strftime('%Y-%m-%d')
        actual = series.get(next_day, {})
        closing = actual.get('4. close')

        eval_date = datetime.utcnow().strftime('%Y-%m-%d')
        filename = EVAL_DIR / f'evaluation-{eval_date}.md'
        lines = [f"# Evaluation - {eval_date}", f"Report evaluated: {report_path.name}"]
        if closing:
            lines.append(f"Actual closing price on {next_day}: {closing}")
        else:
            lines.append(f"No data for {next_day}")
        filename.write_text('\n'.join(lines))
        self.repo.git.add(str(filename))
        self.repo.index.commit(f"Add evaluation report for {eval_date}")
        return filename
