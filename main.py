import sys
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
from watchlist import WatchlistManager


def apply_metrics_to_summary(summary_path: Path, metrics: Dict[str, Dict]):
    """Insert accuracy and calibration info into the summary file."""
    if not summary_path.exists():
        return
    lines = summary_path.read_text().splitlines()
    new_lines: List[str] = []
    current_symbol: str | None = None
    for line in lines:
        new_lines.append(line)
        if line.startswith("Symbol:"):
            parts = line.split()
            current_symbol = parts[1] if len(parts) > 1 else None
        if line.startswith("Insight:"):
            metric = metrics.get(current_symbol or "")
            new_lines.append("")
            if metric and metric.get("accuracy_rate") is not None:
                acc_pct = metric["accuracy_rate"] * 100
                new_lines.append(f"Accuracy trend (last 7 days): {acc_pct:.0f}% accurate")
                avg_conf = metric.get("avg_confidence", 0)
                calib = metric.get("calibration", "")
                new_lines.append(
                    f"Confidence calibration: Avg {avg_conf:.0f}% confidence → {acc_pct:.0f}% accuracy → {calib}"
                )
            else:
                new_lines.append("Accuracy trend (last 7 days): no data")
                new_lines.append("Confidence calibration: no data")
            new_lines.append("")
    summary_path.write_text("\n".join(new_lines))




def gather_flow(query: str = "stock market", commit: bool = True):
    """Generate prediction reports for all symbols in the watchlist."""
    logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
    manager = WatchlistManager()
    entries = manager.load()
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
    manager = WatchlistManager()
    entries = manager.load()
    symbols = [e.get("symbol") for e in entries if e.get("symbol")]
    if symbol:
        symbols = [symbol]
    evaluator = Evaluator()
    eval_path = evaluator.evaluate(symbols, commit=commit)
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

    metrics = {}
    suggestions_path = None
    try:
        from prediction_adjuster import generate_adjustment_file
        metrics, suggestions_path = generate_adjustment_file()
    except Exception as e:
        logging.exception("Adjustment generation failed: %s", e)

    try:
        if metrics:
            apply_metrics_to_summary(summary_path, metrics)
    except Exception as e:
        logging.exception("Failed to update summary with metrics: %s", e)

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
    log_file = Path('history/prediction_accuracy_log.jsonl')
    if log_file.exists():
        repo.git.add(str(log_file))
    if suggestions_path and Path(suggestions_path).exists():
        repo.git.add(str(suggestions_path))
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
