from typing import List

class StockPredictor:
    def predict(self, sentiments: List[float]) -> float:
        """Simple heuristic: average sentiment as proxy for next day movement."""
        if not sentiments:
            return 0.0
        return sum(sentiments) / len(sentiments)
