import sys
import json
import logging
from pathlib import Path
from typing import List, Dict
from datetime import datetime

from git import Repo

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


def gather_flow(query: str = "stock market", commit: bool = True):
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

    report_path = writer.write(results, commit=commit)
    summary_path = writer.write_summary(results, commit=commit)
    print(f"Report generated at {report_path}")
    print(f"Summary generated at {summary_path}")
    return report_path, summary_path


def evaluate_flow(symbol: str | None = None, commit: bool = True):
    if symbol is None:
        entries = _load_watchlist()
        syms = [e.get("symbol") for e in entries if e.get("symbol")]
        symbol = syms[0] if syms else "AAPL"
    evaluator = Evaluator()
    eval_path = evaluator.evaluate(symbol, commit=commit)
    print(f"Evaluation report generated at {eval_path}")
    return eval_path


def stock_forecast_flow() -> None:
    """Run gather and then evaluate previous predictions, committing results at the end."""
    report_path, summary_path = gather_flow(commit=False)
    eval_path = None
    try:
        eval_path = evaluate_flow(commit=False)
    except Exception as e:
        logging.exception("Forecast evaluation failed: %s", e)

    repo = Repo(Path(__file__).resolve().parent)
    repo.git.add(str(report_path))
    repo.git.add(str(summary_path))
    date_str = datetime.utcnow().strftime("%Y-%m-%d")
    eval_json = Path(f"evaluations/evaluation_{date_str}.json")
    eval_summary = Path(f"evaluations/evaluation_summary_{date_str}.txt")
    if eval_path and Path(eval_path).exists():
        repo.git.add(str(eval_path))
    if eval_json.exists():
        repo.git.add(str(eval_json))
    if eval_summary.exists():
        repo.git.add(str(eval_summary))
    repo.index.commit(f"Add forecast results for {date_str}")


def main():
    if len(sys.argv) < 2:
        print('Usage: python main.py [gather|evaluate|stock_forecast|learn_new_stocks]')
        return
    command = sys.argv[1]
    if command == 'gather':
        gather_flow()
    elif command == 'evaluate':
        evaluate_flow()
    elif command == 'stock_forecast':
        stock_forecast_flow()
    elif command == 'learn_new_stocks':
        learn_new_stocks()
    else:
        print(f'Unknown command: {command}')


if __name__ == '__main__':
    main()
