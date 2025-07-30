from pathlib import Path
from watchlist import WatchlistManager


def test_watchlist_load_and_save(tmp_path: Path):
    manager = WatchlistManager(tmp_path / 'wl.json')
    assert manager.load() == []
    data = [{'symbol': 'ABC'}]
    manager.save(data)
    assert manager.load() == data
