import numpy as np


def sharpe_ratio(returns):
    if len(returns) < 2:
        return 0

    return (np.mean(returns) / (np.std(returns) + 1e-8)) * np.sqrt(252)


def max_drawdown(equity):
    peak = np.maximum.accumulate(equity)
    dd = (equity - peak) / (peak + 1e-8)
    return float(dd.min())


def winrate(trades):
    if len(trades) == 0:
        return 0
    return len([t for t in trades if t > 0]) / len(trades)
