import logging
from pathlib import Path
from typing import List, Dict

from gather.news_fetcher import NewsFetcher
from watchlist import WatchlistManager

WATCHLIST_PATH = Path("watchlist.json")


def load_watchlist(path: Path = WATCHLIST_PATH) -> List[Dict]:
    return WatchlistManager(path).load()


def save_watchlist(data: List[Dict], path: Path = WATCHLIST_PATH) -> None:
    WatchlistManager(path).save(data)


def learn_new_stocks(query: str = "stock market") -> None:
    """Discover new stocks from recent news headlines and extend the watchlist."""
    logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

    watchlist = load_watchlist()
    known = {item.get("symbol") for item in watchlist}
    fetcher = NewsFetcher()
    articles = fetcher.fetch(query, page_size=20)

    mapping: Dict[str, tuple[str, List[str]]] = {
        "Broadcom": ("AVGO", ["Broadcom", "VMware"]),
        "Adobe": ("ADBE", ["Adobe", "Photoshop"]),
        "Qualcomm": ("QCOM", ["Qualcomm", "Snapdragon"]),
        "Samsung": ("SSNLF", ["Samsung", "Galaxy"]),
        "Spotify": ("SPOT", ["Spotify"]),
        "Intel": ("INTC", ["Intel", "processor"]),
    }

    added = []
    for art in articles:
        title = art.get("title", "")
        for name, (symbol, keywords) in mapping.items():
            if symbol in known:
                continue
            if name.lower() in title.lower():
                watchlist.append({
                    "symbol": symbol,
                    "keywords": keywords,
                    "discovered": True,
                    "discovery_headline": title,
                })
                known.add(symbol)
                added.append(symbol)
                logging.info("Discovered new stock %s from headline: %s", symbol, title)
                break

    if added:
        save_watchlist(watchlist)
        print("Added new stocks:", ", ".join(added))
    else:
        print("No new stocks discovered.")


if __name__ == "__main__":
    learn_new_stocks()
