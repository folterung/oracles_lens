import sys
from gather.news_fetcher import NewsFetcher
from gather.sentiment_analyzer import SentimentAnalyzer
from predictor.predictor import StockPredictor
from reporting.markdown_reporter import MarkdownReporter
from evaluation.evaluator import Evaluator


def gather_flow(query: str = 'stock market', symbol: str = 'AAPL'):
    news_fetcher = NewsFetcher()
    analyzer = SentimentAnalyzer()
    predictor = StockPredictor()
    reporter = MarkdownReporter()

    news = news_fetcher.fetch(query)
    texts = [item['title'] for item in news]
    insights = analyzer.analyze(texts, symbol)
    prediction = predictor.predict(insights, symbol)
    report_path = reporter.generate_report(news, insights, prediction, symbol)
    print(f"Report generated at {report_path}")


def evaluate_flow(symbol: str = 'AAPL'):
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
