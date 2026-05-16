import numpy as np


def net_position_osc(longs, shorts):
    total = longs + shorts

    if total == 0:
        return 0.0

    return (longs - shorts) / total


def rolling_net_osc(net_longs, net_shorts, window=14):
    """
    cumulative imbalance (stable version)
    """

    n = len(net_longs)
    out = np.zeros(n)

    for i in range(n):
        start = max(0, i - window + 1)

        l = np.sum(net_longs[start : i + 1])
        s = np.sum(net_shorts[start : i + 1])

        out[i] = net_position_osc(l, s)

    return out
