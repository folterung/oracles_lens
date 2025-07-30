import sys
import json
from pathlib import Path
from typing import List, Dict

from gather.news_fetcher import NewsFetcher
from gather.sentiment_analyzer import SentimentAnalyzer
from evaluation.evaluator import Evaluator
from relevance_matcher import RelevanceMatcher
from report_writer import ReportWriter
from learn_new_stocks import learn_new_stocks


def _load_watchlist(path: str = "watchlist.json") -> List[Dict]:
    """Load watchlist entries from JSON."""
    p = Path(path)
    if not p.exists():
        return []
    try:
        data = json.loads(p.read_text())
        if isinstance(data, list):
            return data
    except Exception:
        pass
    return []


def _save_watchlist(entries: List[Dict], path: str = "watchlist.json") -> None:
    Path(path).write_text(json.dumps(entries, indent=2))


def gather_flow(query: str = "stock market") -> None:
    """Generate prediction reports for all symbols in the watchlist."""
    entries = _load_watchlist()
    symbols = [e.get("symbol") for e in entries if e.get("symbol")]
    if not symbols:
        print("Watchlist is empty")
        return

    fetcher = NewsFetcher()
    matcher = RelevanceMatcher()
    analyzer = SentimentAnalyzer()
    writer = ReportWriter()

    for symbol in symbols:
        news = fetcher.fetch(f"{symbol} {query}")
        matched = matcher.match_headlines(news, symbol)
        analyzed = analyzer.analyze(matched)
        weighted = analyzer.weighted_score(analyzed)
        confidence = analyzer.confidence(analyzed)
        report_path = writer.write(symbol, analyzed, weighted, confidence)
        print(f"Report generated for {symbol} at {report_path}")


def evaluate_flow(symbol: str | None = None):
    if symbol is None:
        entries = _load_watchlist()
        syms = [e.get("symbol") for e in entries if e.get("symbol")]
        symbol = syms[0] if syms else "AAPL"
    evaluator = Evaluator()
    eval_path = evaluator.evaluate(symbol)
    print(f"Evaluation report generated at {eval_path}")


def main():
    if len(sys.argv) < 2:
        print('Usage: python main.py [gather|evaluate|learn_new_stocks]')
        return
    command = sys.argv[1]
    if command == 'gather':
        gather_flow()
    elif command == 'evaluate':
        evaluate_flow()
    elif command == 'learn_new_stocks':
        learn_new_stocks()
    else:
        print(f'Unknown command: {command}')


if __name__ == '__main__':
    main()
