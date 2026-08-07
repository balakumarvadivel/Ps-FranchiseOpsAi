from app.services.ai.forecasting import moving_average, linear_regression_forecast


def test_moving_average_smooths_series():
    result = moving_average([10, 20, 30, 40, 50], window=2)
    assert len(result) == 5
    assert result[0] == 10  # first point has nothing to average with
    assert result[1] == 15  # (10+20)/2


def test_forecast_flat_when_insufficient_history():
    result = linear_regression_forecast([100.0], periods_ahead=5)
    assert result["forecast"] == [100.0] * 5
    assert result["confidence"] == 50.0


def test_forecast_projects_upward_trend():
    history = [100.0, 110.0, 120.0, 130.0, 140.0, 150.0]
    result = linear_regression_forecast(history, periods_ahead=3)
    assert len(result["forecast"]) == 3
    # An upward trend should keep projecting upward
    assert result["forecast"][0] > history[-1] - 5
    assert result["forecast"][-1] >= result["forecast"][0]
    assert 0 <= result["confidence"] <= 100


def test_forecast_never_goes_negative():
    history = [10.0, 5.0, 0.0, 0.0]
    result = linear_regression_forecast(history, periods_ahead=5)
    assert all(v >= 0 for v in result["forecast"])
    assert all(v >= 0 for v in result["low"])


def test_forecast_band_ordering():
    history = [50.0, 55.0, 52.0, 58.0, 60.0, 62.0, 61.0]
    result = linear_regression_forecast(history, periods_ahead=4)
    for low, mid, high in zip(result["low"], result["forecast"], result["high"]):
        assert low <= mid <= high
