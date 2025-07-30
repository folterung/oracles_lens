from __future__ import annotations

from datetime import datetime
from typing import List, Dict, Tuple

from textblob import TextBlob
from dateutil import parser


class SentimentAnalyzer:
    """Perform sentiment analysis and compute weighted scores."""

    def analyze(self, items: List[Dict]) -> List[Dict]:
        """Return sentiment info for each relevant news item."""
        results: List[Dict] = []
        for item in items:
            title = item.get("title", "")
            polarity = TextBlob(title).sentiment.polarity
            results.append({
                "title": title,
                "sentiment": float(polarity),
                "relevance_score": float(item.get("relevance_score", 0.0)),
                "keyword": item.get("keyword", ""),
                "publishedAt": item.get("publishedAt"),
            })
        return results

    def weighted_score(self, items: List[Dict]) -> float:
        """Compute relevance and recency weighted sentiment score."""
        now = datetime.utcnow()
        total = 0.0
        weight_sum = 0.0
        for item in items:
            relevance = float(item.get("relevance_score", 0.0))
            ts = item.get("publishedAt")
            recency = 1.0
            if ts:
                try:
                    dt = parser.parse(ts)
                    days = (now - dt).total_seconds() / 86400.0
                    recency = max(0.5, 1 - days / 7)
                except Exception:
                    recency = 1.0
            weight = relevance * recency
            total += float(item.get("sentiment", 0.0)) * weight
            weight_sum += weight
        return total / weight_sum if weight_sum else 0.0

    def confidence(self, items: List[Dict]) -> Tuple[float, str]:
        """Return confidence percentage and label."""
        if not items:
            return 0.0, "Low"
        n = len(items)
        avg_rel = sum(i.get("relevance_score", 0.0) for i in items) / n
        avg_abs_sent = sum(abs(i.get("sentiment", 0.0)) for i in items) / n
        volume = min(n / 5.0, 1.0)
        score = (avg_rel * 0.4 + avg_abs_sent * 0.4 + volume * 0.2) * 100
        label = "High" if score > 66 else "Medium" if score > 33 else "Low"
        return score, label
