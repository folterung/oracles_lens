import sys
from pathlib import Path
from typing import List

from gather.news_fetcher import NewsFetcher
from gather.sentiment_analyzer import SentimentAnalyzer
from evaluation.evaluator import Evaluator
from relevance_matcher import RelevanceMatcher
from report_writer import ReportWriter


def _load_watchlist(path: str = "watchlist.txt") -> List[str]:
    if not Path(path).exists():
        return []
    return [line.strip() for line in Path(path).read_text().splitlines() if line.strip()]


def gather_flow(query: str = "stock market"):
    """Generate prediction reports for all symbols in the watchlist."""
    symbols = _load_watchlist()
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
        symbols = _load_watchlist()
        symbol = symbols[0] if symbols else "AAPL"
    evaluator = Evaluator()
    eval_path = evaluator.evaluate(symbol)
    print(f"Evaluation report generated at {eval_path}")


def main():
    if len(sys.argv) < 2:
        print('Usage: python main.py [gather|evaluate]')
        return
    command = sys.argv[1]
    if command == 'gather':
        gather_flow()
    elif command == 'evaluate':
        evaluate_flow()
    else:
        print(f'Unknown command: {command}')


if __name__ == '__main__':
    main()
