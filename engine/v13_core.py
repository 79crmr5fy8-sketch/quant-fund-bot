import numpy as np


# =========================================
# VOLATILITY ESTIMATOR
# =========================================
def get_volatility(prices, i, window=20):
    start = max(1, i - window)
    segment = prices[start : i + 1]

    if len(segment) < 2:
        return 0.01

    rets = np.diff(segment) / segment[:-1]
    vol = np.std(rets)

    return max(vol, 1e-6)


# =========================================
# DRAWDOWN TRACKER
# =========================================
def compute_drawdown(equity_curve):
    peak = np.maximum.accumulate(equity_curve)
    dd = (equity_curve - peak) / peak
    return dd[-1]


# =========================================
# POSITION SIZING ENGINE
# =========================================
def position_size(equity, vol, regime_strength, base_risk=0.02):

    # inverse volatility targeting
    vol_scale = 1.0 / (1.0 + vol * 50)

    # regime boost (trend = more risk allowed)
    regime_scale = 0.5 + regime_strength

    size = equity * base_risk * vol_scale * regime_scale

    return np.clip(size, 0, equity * 0.1)


# =========================================
# KILL SWITCH
# =========================================
def risk_kill_switch(drawdown, threshold=-0.12):

    if drawdown < threshold:
        return True
    return False
