import json
from pathlib import Path
from typing import List, Dict

from gather.news_fetcher import NewsFetcher

WATCHLIST_PATH = Path("watchlist.json")


def load_watchlist(path: Path = WATCHLIST_PATH) -> List[Dict]:
    if path.exists():
        try:
            return json.loads(path.read_text())
        except Exception:
            return []
    return []


def save_watchlist(data: List[Dict], path: Path = WATCHLIST_PATH) -> None:
    path.write_text(json.dumps(data, indent=2))


def learn_new_stocks(query: str = "stock market") -> None:
    """Discover new stocks from recent news headlines and extend the watchlist."""
    watchlist = load_watchlist()
    known = {item.get("symbol") for item in watchlist}
    fetcher = NewsFetcher()
    articles = fetcher.fetch(query, page_size=20)

    mapping = {
        "Broadcom": "AVGO",
        "Adobe": "ADBE",
        "Qualcomm": "QCOM",
        "Samsung": "SSNLF",
        "Spotify": "SPOT",
        "Intel": "INTC",
    }

    added = []
    for art in articles:
        title = art.get("title", "")
        for name, symbol in mapping.items():
            if symbol in known:
                continue
            if name.lower() in title.lower():
                watchlist.append({"symbol": symbol, "discovery_reason": title})
                known.add(symbol)
                added.append(symbol)
                break

    if added:
        save_watchlist(watchlist)
        print("Added new stocks:", ", ".join(added))
    else:
        print("No new stocks discovered.")


if __name__ == "__main__":
    learn_new_stocks()
