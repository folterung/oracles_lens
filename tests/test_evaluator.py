import json
from datetime import datetime
from pathlib import Path
import types

import evaluation.evaluator as evaluator_mod
from evaluation.evaluator import Evaluator


class DummyCommitter:
    def add_and_commit(self, path: Path, message: str) -> None:
        pass


def test_fetch_actual_direction_up(monkeypatch):
    evalr = Evaluator(stock_api_key="k", committer=DummyCommitter())
    data = {
        "Time Series (Daily)": {
            "2025-07-31": {"4. close": "101"},
            "2025-07-30": {"4. close": "100"},
        }
    }

    class Resp:
        def raise_for_status(self):
            pass
        def json(self):
            return data

    def fake_get(url, params, timeout):
        return Resp()

    monkeypatch.setattr(evaluator_mod, "requests", types.SimpleNamespace(get=fake_get))
    direction = evalr._fetch_actual_direction("ABC", datetime(2025, 7, 30))
    assert direction == "up"


def test_evaluate_creates_file(monkeypatch, tmp_path):
    report = {"date": "2025-07-30", "results": [{"symbol": "ABC", "prediction": {"direction": "up", "confidence": {"value": 70}}}]}
    report_path = tmp_path / "report.json"
    report_path.write_text(json.dumps(report))
    hist_path = tmp_path / "history.jsonl"
    monkeypatch.setattr(evaluator_mod, "HISTORY_LOG", hist_path)
    monkeypatch.setattr(Evaluator, "_previous_report", lambda self: report_path)
    monkeypatch.setattr(Evaluator, "_fetch_actual_direction", lambda self, s, d: "down")
    monkeypatch.setattr(evaluator_mod, "EVAL_DIR", tmp_path)
    evalr = Evaluator(stock_api_key="k", committer=DummyCommitter())
    out = evalr.evaluate(["ABC"], commit=False)
    assert out.exists()
    data = out.read_text()
    assert "ABC" in data
    assert hist_path.exists()
