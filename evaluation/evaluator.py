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

    def evaluate(self, symbol: str, commit: bool = True):
        report_path = self._latest_report()
        parts = report_path.stem.split('-')
        date_str = '-'.join(parts[-3:])
        report_date = datetime.strptime(date_str, '%Y-%m-%d')

        # extract predicted movement score from report
        predicted_value = 0.0
        with open(report_path, 'r') as f:
            for line in f:
                if line.lower().startswith('predicted movement score'):
                    try:
                        predicted_value = float(line.split(':')[-1].strip())
                    except ValueError:
                        predicted_value = 0.0
                    break

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
        closing_next = actual.get('4. close')
        prev = series.get(report_date.strftime('%Y-%m-%d'), {})
        closing_prev = prev.get('4. close')

        predicted_direction = 'up' if predicted_value > 0.05 else 'down' if predicted_value < -0.05 else 'neutral'
        actual_direction = None
        normalized_delta = None
        if closing_next and closing_prev:
            try:
                next_val = float(closing_next)
                prev_val = float(closing_prev)
                delta = next_val - prev_val
                normalized_delta = delta / prev_val if prev_val else 0.0
                if delta > 0:
                    actual_direction = 'up'
                elif delta < 0:
                    actual_direction = 'down'
                else:
                    actual_direction = 'neutral'
            except ValueError:
                pass

        eval_date = datetime.utcnow().strftime('%Y-%m-%d')
        filename = EVAL_DIR / f'evaluation-{eval_date}.md'
        lines = [f"# Evaluation - {eval_date}", f"Report evaluated: {report_path.name}"]
        if closing_next:
            lines.append(f"Actual closing price on {next_day}: {closing_next}")
        else:
            lines.append(f"No data for {next_day}")

        if closing_prev:
            lines.append(f"Previous close on {report_date.strftime('%Y-%m-%d')}: {closing_prev}")

        if normalized_delta is not None:
            actual_delta = float(closing_next) - float(closing_prev)
            lines.append(f"Actual closing delta: {actual_delta:+.4f}")

        if actual_direction:
            lines.append(f"Actual direction: {actual_direction}")
        else:
            lines.append("Actual direction: unknown")

        lines.append(f"Prediction score: {predicted_value:+.4f}")
        lines.append(f"Predicted direction: {predicted_direction}")
        if actual_direction:
            correct = actual_direction == predicted_direction
            lines.append(f"Directional accuracy: {correct}")
            if normalized_delta is not None:
                delta_error = abs(predicted_value - normalized_delta)
                lines.append(f"Delta error: {delta_error:.4f}")

        filename.write_text('\n'.join(lines))
        if commit:
            self.repo.git.add(str(filename))
            self.repo.index.commit(f"Add evaluation report for {eval_date}")
        return filename
