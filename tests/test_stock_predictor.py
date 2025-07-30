from predictor.predictor import StockPredictor


def test_predict_weighted_average():
    predictor = StockPredictor()
    insights = [
        {'affected_entities': ['XYZ'], 'sentiment': 0.5, 'confidence_score': 60},
        {'affected_entities': ['XYZ'], 'sentiment': -0.5, 'confidence_score': 40},
    ]
    result = predictor.predict(insights, 'XYZ')
    # weighted average: (0.5*60 + (-0.5*40)) / (60+40) = 0.1
    assert round(result, 2) == 0.10


def test_predict_no_relevant_insights():
    predictor = StockPredictor()
    insights = [{'affected_entities': ['ABC'], 'sentiment': 1.0, 'confidence_score': 100}]
    assert predictor.predict(insights, 'XYZ') == 0.0
