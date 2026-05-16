import numpy as np


def detect_regime(prices, window=50):
    if len(prices) < window + 2:
        return "CHOP"

    recent = np.array(prices[-window:])

    returns = np.diff(recent) / (recent[:-1] + 1e-8)

    vol = np.std(returns)
    drift = abs(recent[-1] - recent[0]) / (np.mean(recent) + 1e-8)

    path = np.sum(np.abs(np.diff(recent)))
    net = abs(recent[-1] - recent[0])
    efficiency = net / (path + 1e-8)

    score = 0

    if efficiency > 0.30:
        score += 1
    if drift > 0.007:
        score += 1
    if vol < 0.004:
        score += 1

    return "TREND" if score >= 2 else "CHOP"


def regime_weight(regime):
    if regime == "TREND":
        return 1.30
    if regime == "CHOP":
        return 0.70
    return 1.0
