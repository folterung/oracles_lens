from report_writer import ReportWriter


def test_recommendation_and_turnover():
    writer = ReportWriter()
    rec, turn = writer.recommendation_and_turnover(0.3, 70, 'High')
    assert rec == 'BUY'
    assert turn == '2-3 days'
    rec, turn = writer.recommendation_and_turnover(-0.3, 50, 'Low')
    assert rec == 'AVOID'
    assert turn == '7-10 days'
    rec, turn = writer.recommendation_and_turnover(0.0, 40, 'Medium')
    assert rec == 'HOLD'
    assert turn == '4-7 days'
