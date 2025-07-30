from pathlib import Path
from prediction_adjuster import analyze


def test_analyze_metrics(tmp_path: Path):
    data = [
        {"date": "2025-07-29", "symbol": "ABC", "predicted_direction": "up", "confidence": 70, "accuracy": True},
        {"date": "2025-07-30", "symbol": "ABC", "predicted_direction": "up", "confidence": 80, "accuracy": False},
        {"date": "2025-07-30", "symbol": "XYZ", "predicted_direction": "down", "confidence": 50, "accuracy": True},
    ]
    log_path = tmp_path / "log.jsonl"
    log_path.write_text("\n".join([__import__('json').dumps(d) for d in data]))
    metrics = analyze(log_path=log_path, days=7)
    assert metrics["ABC"]["accuracy_rate"] == 0.5
    assert metrics["XYZ"]["accuracy_rate"] == 1.0
