from typing import List, Dict

class StockPredictor:
    def predict(self, insights: List[Dict], symbol: str) -> float:
        """Return confidence-weighted sentiment for the specified symbol."""
        if not insights:
            return 0.0

        # filter insights referencing the target symbol
        symbol_upper = symbol.upper()
        relevant = []
        for item in insights:
            entities = item.get('affected_entities', []) or []
            entities_upper = [str(e).upper() for e in entities]
            if symbol_upper in entities_upper:
                relevant.append(item)

        if not relevant:
            return 0.0

        numerator = 0.0
        denominator = 0.0
        for item in relevant:
            sentiment = float(item.get('sentiment', 0.0))
            confidence = float(item.get('confidence_score', 0.0))
            numerator += sentiment * confidence
            denominator += confidence

        if denominator == 0:
            return 0.0

        return numerator / denominator
