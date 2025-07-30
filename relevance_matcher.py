import difflib
from typing import Dict, List, Tuple

DEFAULT_KEYWORDS: Dict[str, List[str]] = {
    "AAPL": ["Apple", "iPhone", "iPad", "Mac", "MacBook", "AirPods"],
    "MSFT": ["Microsoft", "Windows", "Azure", "Xbox", "Surface"],
    "GOOGL": ["Google", "Alphabet", "Android", "YouTube"],
    "AMZN": ["Amazon", "AWS", "Prime", "Kindle"],
    "TSLA": ["Tesla", "Elon Musk", "Model", "Cybertruck"],
    "NVDA": ["Nvidia", "GPU", "GeForce", "RTX"],
    "META": ["Meta", "Facebook", "Instagram", "WhatsApp"],
    "NFLX": ["Netflix", "streaming", "Stranger Things"],
    "JPM": ["JPMorgan", "Chase", "banking"],
    "IBM": ["IBM", "Big Blue", "Watson"],
}

class RelevanceMatcher:
    """Score how relevant a headline is to a stock symbol."""

    def __init__(self, keyword_map: Dict[str, List[str]] | None = None):
        self.keyword_map = keyword_map or DEFAULT_KEYWORDS

    def score(self, headline: str, symbol: str) -> Tuple[float, str]:
        """Return (score, keyword) for the given headline and symbol."""
        text = headline.lower()
        symbol = symbol.upper()
        keywords = [symbol] + self.keyword_map.get(symbol, [])
        best_score = 0.0
        best_kw = ""
        for kw in keywords:
            kw_lower = kw.lower()
            if kw_lower in text:
                score = 1.0
            else:
                score = difflib.SequenceMatcher(None, kw_lower, text).ratio()
            if score > best_score:
                best_score = score
                best_kw = kw
        return best_score, best_kw

    def match_headlines(self, news_items: List[dict], symbol: str, threshold: float = 0.3) -> List[dict]:
        """Return news items with relevance >= threshold."""
        matches: List[dict] = []
        for item in news_items:
            title = item.get("title", "")
            score, kw = self.score(title, symbol)
            if score >= threshold:
                matches.append({
                    "title": title,
                    "relevance_score": score,
                    "keyword": kw,
                    "publishedAt": item.get("publishedAt"),
                })
        matches.sort(key=lambda x: x["relevance_score"], reverse=True)
        return matches
