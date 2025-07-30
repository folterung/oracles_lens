import sys
import json
import logging
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
    except Exception as e:
        logging.exception("Failed to parse watchlist: %s", e)
    return []


def _save_watchlist(entries: List[Dict], path: str = "watchlist.json") -> None:
    Path(path).write_text(json.dumps(entries, indent=2))


def gather_flow(query: str = "stock market") -> None:
    """Generate prediction reports for all symbols in the watchlist."""
    logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
    entries = _load_watchlist()
    if not entries:
        print("Watchlist is empty")
        return

    symbol_keywords = {e.get("symbol"): e.get("keywords", []) for e in entries if e.get("symbol")}
    symbol_company = {e.get("symbol"): (e.get("keywords") or [""])[0] for e in entries if e.get("symbol")}

    fetcher = NewsFetcher()
    matcher = RelevanceMatcher(keyword_map=symbol_keywords)
    analyzer = SentimentAnalyzer()
    writer = ReportWriter()

    results = []
    for entry in entries:
        symbol = entry.get("symbol")
        if not symbol:
            continue
        logging.info("Processing %s", symbol)
        try:
            news = fetcher.fetch(f"{symbol} {query}")
        except Exception as e:
            logging.exception("Failed to fetch news for %s: %s", symbol, e)
            news = []

        matched = matcher.match_headlines(news, symbol)
        try:
            analyzed = analyzer.analyze(matched)
        except Exception as e:
            logging.exception("Sentiment analysis failed for %s: %s", symbol, e)
            analyzed = []

        weighted = analyzer.weighted_score(analyzed)
        confidence = analyzer.confidence(analyzed)
        direction = "up" if weighted > 0 else "down" if weighted < 0 else "neutral"

        results.append({
            "symbol": symbol,
            "company": symbol_company.get(symbol, ""),
            "headlines": [m.get("title", "") for m in matched],
            "prediction": {
                "score": weighted,
                "direction": direction,
                "confidence": {
                    "label": confidence[1],
                    "value": confidence[0],
                },
            },
        })

    report_path = writer.write(results)
    summary_path = writer.write_summary(results)
    print(f"Report generated at {report_path}")
    print(f"Summary generated at {summary_path}")


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
