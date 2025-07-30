import pytest
from relevance_matcher import RelevanceMatcher


def test_score_exact_match():
    matcher = RelevanceMatcher({'ABC': ['Alpha']})
    score, kw = matcher.score('Alpha launches new product', 'ABC')
    assert score == 1.0
    assert kw == 'Alpha'


def test_match_headlines_threshold():
    matcher = RelevanceMatcher({'ABC': ['Alpha']})
    items = [
        {'title': 'Alpha announces earnings', 'publishedAt': '2025-07-30'},
        {'title': 'Other company news', 'publishedAt': '2025-07-30'},
    ]
    matches = matcher.match_headlines(items, 'ABC', threshold=0.5)
    assert len(matches) == 1
    assert matches[0]['title'] == 'Alpha announces earnings'
