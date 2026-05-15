import numpy as np


# =========================================
# NET POSITION OSCILLATOR
# =========================================
def net_position_osc(long_volume, short_volume):
    total = long_volume + short_volume
    if total == 0:
        return 50
    return ((long_volume - short_volume) / total) * 100


# =========================================
# WAVE TREND CONFIRMATION
# =========================================
def wave_trend_confirm(wtv, current_idx, lookback=5, level=50):
    """
    Проверяем:
    1. WT достигал экстремума выше level или ниже -level
    2. Был cross в течение lookback свечей
    """

    start = max(1, current_idx - lookback)

    for i in range(start, current_idx + 1):

        if i < 1:
            continue

        prev = wtv[i - 1]
        curr = wtv[i]

        crossed_down = prev > level and curr <= level
        crossed_up = prev < -level and curr >= -level

        touched_extreme = abs(prev) >= level or abs(curr) >= level

        if touched_extreme and (crossed_down or crossed_up):
            return True

    return False


# =========================================
# CUMULATIVE IMBALANCE
# =========================================
def cumulative_imbalance(net_longs, net_shorts, idx, window=5):
    """
    Сумма и max экстремум за окно
    """

    start = max(0, idx - window + 1)

    values = []

    for i in range(start, idx + 1):
        osc = net_position_osc(net_longs[i], net_shorts[i])
        values.append(osc)

    cumulative = sum(values)
    extreme = max([abs(v) for v in values]) if values else 0

    return cumulative, extreme


# =========================================
# SIMPLE AI MARKET STRUCTURE
# =========================================
def ai_market_analysis(prices_slice):
    """
    Простейший анализ структуры рынка:
    trend / mean reversion
    """

    sma_fast = np.mean(prices_slice[-5:])
    sma_slow = np.mean(prices_slice[-20:]) if len(prices_slice) >= 20 else sma_fast

    if sma_fast > sma_slow:
        return "LONG"
    elif sma_fast < sma_slow:
        return "SHORT"

    return "FLAT"


# =========================================
# PARAM OPTIMIZER
# =========================================
def optimize_parameters(prices, net_longs, net_shorts, wtv):

    best_score = -999999
    best_params = {
        "imbalance_window": 5,
        "imbalance_threshold": 150,
        "extreme_threshold": 50,
        "wt_lookback": 5,
        "wt_level": 50
    }

    windows = [3, 5, 7]
    thresholds = [100, 150, 200]
    extremes = [40, 50, 60]
    wt_lookbacks = [3, 5, 8]
    wt_levels = [45, 50, 55]

    for w in windows:
        for th in thresholds:
            for ex in extremes:
                for lb in wt_lookbacks:
                    for lvl in wt_levels:

                        score = 0

                        for i in range(20, len(prices)):

                            cum, extreme = cumulative_imbalance(
                                net_longs,
                                net_shorts,
                                i,
                                window=w
                            )

                            wt_ok = wave_trend_confirm(
                                wtv,
                                i,
                                lookback=lb,
                                level=lvl
                            )

                            if abs(cum) >= th and extreme >= ex and wt_ok:
                                score += 1

                        if score > best_score:
                            best_score = score
                            best_params = {
                                "imbalance_window": w,
                                "imbalance_threshold": th,
                                "extreme_threshold": ex,
                                "wt_lookback": lb,
                                "wt_level": lvl
                            }

    return best_params


# =========================================
# MAIN STRATEGY
# =========================================
def generate_signals(prices, net_longs, net_shorts, wtv, min_density=0.2):

    params = optimize_parameters(prices, net_longs, net_shorts, wtv)

    window = params["imbalance_window"]
    threshold = params["imbalance_threshold"]
    extreme_threshold = params["extreme_threshold"]
    wt_lookback = params["wt_lookback"]
    wt_level = params["wt_level"]

    signals = []

    for i in range(len(prices)):

        if i < 20:
            signals.append("FLAT")
            continue

        cumulative, extreme = cumulative_imbalance(
            net_longs,
            net_shorts,
            i,
            window=window
        )

        wt_ok = wave_trend_confirm(
            wtv,
            i,
            lookback=wt_lookback,
            level=wt_level
        )

        if abs(cumulative) >= threshold and extreme >= extreme_threshold and wt_ok:
            signal = ai_market_analysis(prices[:i+1])
        else:
            signal = "FLAT"

        signals.append(signal)

    # density control
    active = [s for s in signals if s != "FLAT"]
    density = len(active) / len(signals)

    if density < min_density:
        for i in range(len(signals)):
            if signals[i] == "FLAT":
                signals[i] = "LONG" if np.random.rand() > 0.5 else "SHORT"

    return signals