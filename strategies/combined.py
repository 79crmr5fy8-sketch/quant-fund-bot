import numpy as np


# =========================================
# SAFE NORMALIZATION
# =========================================
def safe_tanh(x):
    return np.tanh(np.clip(x, -10, 10))


# =========================================
# REGIME DETECTION (trend vs chop)
# =========================================
def detect_regime(prices, idx, window=20):
    start = max(0, idx - window)
    slice_ = prices[start : idx + 1]

    if len(slice_) < 5:
        return 0.5  # neutral

    returns = np.diff(slice_)
    trend_strength = abs(np.mean(returns)) / (np.std(returns) + 1e-8)

    # normalize to 0..1
    regime = 1 / (1 + np.exp(-trend_strength))
    return float(np.clip(regime, 0.0, 1.0))


# =========================================
# SIGNAL GENERATION
# =========================================
def generate_signals(prices, net_longs, net_shorts, wtv):
    n = min(len(prices), len(net_longs), len(net_shorts), len(wtv))

    signals = []

    for i in range(n):

        price = prices[i]

        # ===============================
        # imbalance
        # ===============================
        long = net_longs[i]
        short = net_shorts[i]

        denom = long + short + 1e-8
        imbalance = (long - short) / denom

        # ===============================
        # wave trend
        # ===============================
        wt = wtv[i]

        wt_signal = 0.0
        if wt > 50:
            wt_signal = 1
        elif wt < -50:
            wt_signal = -1

        # ===============================
        # regime filter
        # ===============================
        regime = detect_regime(prices, i)

        # ===============================
        # SCORE (CORE FIX)
        # ===============================
        score = imbalance * 1.5 + wt_signal * 1.0

        # regime scaling (IMPORTANT FIX)
        score *= 0.5 + regime

        # clamp stability
        score = safe_tanh(score * 2.0)

        # ===============================
        # SIGNAL LOGIC
        # ===============================
        if score > 0.35:
            signals.append("LONG")
        elif score < -0.35:
            signals.append("SHORT")
        else:
            signals.append("FLAT")

    return signals
