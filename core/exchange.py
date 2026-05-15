import numpy as np

def detect_regime(closes):

    returns = np.diff(closes)
    volatility = np.std(returns)
    trend = (closes[-1] - closes[-20]) / closes[-20]

    vol_threshold = np.std(closes) * 0.02

    if volatility > vol_threshold * 3:
        return "VOLATILE"

    if abs(trend) < 0.02:
        return "RANGE"

    if trend > 0:
        return "TRENDING_UP"

    return "TRENDING_DOWN"