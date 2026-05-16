import numpy as np


def ema(data, period):
    alpha = 2 / (period + 1)
    out = np.zeros_like(data)

    out[0] = data[0]

    for i in range(1, len(data)):
        out[i] = alpha * data[i] + (1 - alpha) * out[i - 1]

    return out


def wave_trend(close, channel=10, avg=21, signal=4):
    """
    simplified LazyBear WT
    """

    ap = close

    esa = ema(ap, channel)
    d = ema(np.abs(ap - esa), channel)

    ci = (ap - esa) / (0.015 * d + 1e-8)

    tci = ema(ci, avg)
    wt = ema(tci, signal)

    # normalize to 0-100 scale
    wt_norm = 50 + (wt * 10)

    return np.clip(wt_norm, 0, 100)
