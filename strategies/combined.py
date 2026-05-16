import numpy as np
from strategies.regime import detect_regime, regime_weight


def generate_signals(prices, net_longs, net_shorts, wtv):

    signals = []

    n = min(len(prices), len(net_longs), len(net_shorts), len(wtv))

    # буфер для стабильной нормализации (ключевой фикс)
    score_window = []

    for i in range(n):

        regime = detect_regime(prices[: i + 1])
        weight = regime_weight(regime)

        long_v = net_longs[i]
        short_v = net_shorts[i]

        total = long_v + short_v

        imb = 0.0 if total == 0 else (long_v - short_v) / total

        wt = (wtv[i] - 50) / 50

        # =========================
        # RAW SCORE
        # =========================
        score = (0.9 * imb + 0.7 * wt) * weight

        # -------------------------
        # CLIP (убираем выбросы)
        # -------------------------
        score = np.clip(score, -1.0, 1.0)

        # =========================
        # STABLE NORMALIZATION (FIX #2)
        # =========================
        score_window.append(score)

        if len(score_window) > 50:
            score_window.pop(0)

        mean = np.mean(score_window)
        std = np.std(score_window) + 1e-8

        z = (score - mean) / std

        # =========================
        # SAFE SIGMOID (FIX #1)
        # =========================
        z = np.clip(z, -10, 10)
        prob = 1 / (1 + np.exp(-z))

        # =========================
        # DECISION LOGIC
        # =========================
        if prob > 0.62:
            signals.append("LONG")

        elif prob < 0.38:
            signals.append("SHORT")

        else:
            signals.append("FLAT")

    return signals
