from datetime import datetime, timedelta
from gather.sentiment_analyzer import SentimentAnalyzer


def test_weighted_score_prefers_recent():
    analyzer = SentimentAnalyzer()
    now = datetime.utcnow()
    items = [
        {'sentiment': 0.8, 'relevance_score': 1.0, 'publishedAt': now.isoformat()},
        {'sentiment': -0.8, 'relevance_score': 1.0, 'publishedAt': (now - timedelta(days=10)).isoformat()},
    ]
    score = analyzer.weighted_score(items)
    assert score > 0


def test_confidence_scoring():
    analyzer = SentimentAnalyzer()
    items = [{'sentiment': 0.5, 'relevance_score': 0.5} for _ in range(3)]
    value, label = analyzer.confidence(items)
    assert 0 <= value <= 100
    assert label in {'High', 'Medium', 'Low'}
