import numpy as np

# ===========================
# 1. Генерация сигнала LONG / SHORT / FLAT
# ===========================
def generate_signal(closes):
    """
    Простая логика:
    - если короткая MA > длинная MA → LONG
    - если короткая MA < длинная MA → SHORT
    - иначе FLAT
    """
    if len(closes) < 20:
        return "FLAT"  # недостаточно данных

    short_ma = np.mean(closes[-5:])
    long_ma = np.mean(closes[-20:])

    if short_ma > long_ma:
        return "LONG"
    elif short_ma < long_ma:
        return "SHORT"
    else:
        return "FLAT"


# ===========================
# 2. Расчёт confidence
# ===========================
def score(closes):
    """
    Возвращает "уверенность" сигнала в %
    Основывается на:
    - тренде (короткая vs длинная MA)
    - momentum
    """
    if len(closes) < 20:
        return 0  # недостаточно данных

    short_ma = np.mean(closes[-5:])
    long_ma = np.mean(closes[-20:])

    trend = (short_ma - long_ma) / long_ma

    momentum = (closes[-1] - closes[-10]) / closes[-10]

    # базовая уверенность
    conf = abs(trend) * 100 + abs(momentum) * 80

    # ограничиваем 0–100%
    conf = max(min(conf, 100), 0)

    return round(conf, 2)