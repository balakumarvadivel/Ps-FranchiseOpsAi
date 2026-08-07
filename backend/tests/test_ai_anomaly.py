from app.services.ai.anomaly import zscore_anomalies, iqr_anomalies, risk_score_from_audit


def test_zscore_flags_obvious_outlier():
    series = [100, 102, 98, 101, 99, 100, 500]  # last value is way off
    flags = zscore_anomalies(series, threshold=2.0)
    assert flags[-1] is True
    assert sum(flags) == 1


def test_zscore_no_flags_on_uniform_series():
    series = [50, 51, 49, 50, 50, 51]
    flags = zscore_anomalies(series)
    assert not any(flags)


def test_zscore_short_series_returns_no_flags():
    assert zscore_anomalies([1, 2]) == [False, False]


def test_iqr_flags_outlier():
    series = [10, 12, 11, 13, 12, 11, 90]
    flags = iqr_anomalies(series)
    assert flags[-1] is True


def test_risk_score_increases_with_violations():
    low_risk = risk_score_from_audit(compliance_score=95, violation_count=0, critical_violations=0)
    high_risk = risk_score_from_audit(compliance_score=40, violation_count=5, critical_violations=2)
    assert 0 <= low_risk <= 100
    assert 0 <= high_risk <= 100
    assert high_risk > low_risk


def test_risk_score_capped_at_100():
    score = risk_score_from_audit(compliance_score=0, violation_count=50, critical_violations=50)
    assert score <= 100.0
