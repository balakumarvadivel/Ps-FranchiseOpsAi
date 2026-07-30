"""
Anomaly / Risk / Fraud Detection
--------------------------------
Two classic, explainable statistical techniques:
  - Z-score: flags points far from the mean (good for roughly normal data,
    e.g. daily revenue).
  - IQR (interquartile range): more robust to outliers, used for smaller or
    skewed samples (e.g. audit compliance scores).
"""
import statistics
from typing import List


def zscore_anomalies(series: List[float], threshold: float = 2.0) -> List[bool]:
    if len(series) < 3:
        return [False] * len(series)
    mean = statistics.mean(series)
    stdev = statistics.pstdev(series) or 1e-9
    return [abs((x - mean) / stdev) > threshold for x in series]


def iqr_anomalies(series: List[float]) -> List[bool]:
    if len(series) < 4:
        return [False] * len(series)
    sorted_vals = sorted(series)
    n = len(sorted_vals)
    q1 = sorted_vals[n // 4]
    q3 = sorted_vals[(3 * n) // 4]
    iqr = q3 - q1 or 1e-9
    lower, upper = q1 - 1.5 * iqr, q3 + 1.5 * iqr
    return [x < lower or x > upper for x in series]


def risk_score_from_audit(compliance_score: float, violation_count: int, critical_violations: int) -> float:
    """
    Simple weighted risk score (0-100, higher = riskier) combining low
    compliance with the volume/severity of violations found.
    """
    compliance_risk = max(0.0, 100 - compliance_score)
    violation_risk = min(100.0, violation_count * 8)
    critical_risk = min(100.0, critical_violations * 20)
    score = 0.4 * compliance_risk + 0.3 * violation_risk + 0.3 * critical_risk
    return round(min(100.0, score), 1)
