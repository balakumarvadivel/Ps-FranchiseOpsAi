"""
Revenue / Sales Forecasting
---------------------------
Implemented with plain least-squares linear regression (no numpy/pandas
dependency required) over a historical time series, plus a moving-average
smoothing pass. This is intentionally simple and explainable: the forecast
is `trend line + residual-based confidence band`, which is easy to defend
in a project viva. Swap `linear_regression_forecast` for Prophet/ARIMA later
without changing the function signature used by routers.
"""
import math
from typing import List, Tuple


def moving_average(series: List[float], window: int = 3) -> List[float]:
    if len(series) < window:
        return series[:]
    out = []
    for i in range(len(series)):
        lo = max(0, i - window + 1)
        out.append(sum(series[lo:i + 1]) / (i - lo + 1))
    return out


def _least_squares(series: List[float]) -> Tuple[float, float]:
    """Returns (slope, intercept) for y = slope*x + intercept."""
    n = len(series)
    xs = list(range(n))
    x_mean = sum(xs) / n
    y_mean = sum(series) / n

    numerator = sum((xs[i] - x_mean) * (series[i] - y_mean) for i in range(n))
    denominator = sum((xs[i] - x_mean) ** 2 for i in range(n)) or 1e-9
    slope = numerator / denominator
    intercept = y_mean - slope * x_mean
    return slope, intercept


def _residual_std(series: List[float], slope: float, intercept: float) -> float:
    n = len(series)
    residuals = [series[i] - (slope * i + intercept) for i in range(n)]
    variance = sum(r ** 2 for r in residuals) / max(1, n - 1)
    return math.sqrt(variance)


def linear_regression_forecast(history: List[float], periods_ahead: int) -> dict:
    """
    history: chronological list of past period totals (e.g. daily revenue)
    Returns forecast points with a simple confidence band and a 0-100
    confidence score derived from how tight the residuals are relative
    to the mean (lower relative noise -> higher confidence).
    """
    if len(history) < 2:
        flat = history[-1] if history else 0.0
        return {
            "forecast": [flat] * periods_ahead,
            "low": [flat * 0.9] * periods_ahead,
            "high": [flat * 1.1] * periods_ahead,
            "confidence": 50.0,
        }

    smoothed = moving_average(history, window=min(3, len(history)))
    slope, intercept = _least_squares(smoothed)
    std = _residual_std(smoothed, slope, intercept)

    n = len(history)
    forecast, low, high = [], [], []
    for step in range(1, periods_ahead + 1):
        point = slope * (n - 1 + step) + intercept
        point = max(0.0, point)
        forecast.append(round(point, 2))
        low.append(round(max(0.0, point - 1.28 * std), 2))   # ~80% band
        high.append(round(point + 1.28 * std, 2))

    mean_val = sum(history) / n or 1.0
    noise_ratio = std / mean_val
    confidence = max(40.0, min(95.0, 95 - noise_ratio * 100))

    return {
        "forecast": forecast,
        "low": low,
        "high": high,
        "confidence": round(confidence, 1),
        "growth_percent": round(((forecast[-1] - history[-1]) / history[-1]) * 100, 2) if history[-1] else 0.0,
    }
