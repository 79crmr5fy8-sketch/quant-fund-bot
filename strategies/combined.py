import numpy as np

# ================= Net Position Oscillator =================
def net_position_osc(long_volume, short_volume):
    total = long_volume + short_volume
    if total == 0:
        return 50  # нейтрально
    return (long_volume / total) * 100  # значение 0-100


# ================= WaveTrend Cross =================
def wave_trend_cross(wt_values, level=50):
    if len(wt_values) < 2:
        return False
    return (wt_values[-2] < level <= wt_values[-1]) or (wt_values[-2] > level >= wt_values[-1])


# ================= AI Market Analysis =================
def ai_market_analysis(prices_slice, net_longs_slice, net_shorts_slice, wtv_slice):
    """
    Здесь можно подключить реальный AI (например OpenAI API).
    Для демонстрации: простой эвристический алгоритм.
    """
    # Простейший пример: если цена выше среднего + дисбаланс > 60 → LONG
    avg_price = np.mean(prices_slice)
    current_price = prices_slice[-1]
    np_osc = net_position_osc(net_longs_slice[-1], net_shorts_slice[-1])

    if current_price > avg_price and np_osc > 60:
        return "LONG"
    elif current_price < avg_price and np_osc < 40:
        return "SHORT"
    else:
        return "FLAT"


# ================= Combined Strategy =================
def generate_signals(prices, net_longs, net_shorts, wtv, min_density=0.2):
    """
    prices: массив цен OHLCV
    net_longs: массив длинных позиций
    net_shorts: массив коротких позиций
    wtv: WaveTrend значения
    """
    signals = []
    n = len(prices)

    for i in range(n):
        # 1. Рассчёт Net Position Oscillator
        np_osc = net_position_osc(net_longs[i], net_shorts[i])

        # 2. WaveTrend Cross
        wt_cross = wave_trend_cross(wtv[:i+1], level=50)

        # 3. Предварительный фильтр
        if np_osc > 50 and wt_cross:
            # Подключаем AI анализ
            signal = ai_market_analysis(prices[:i+1], net_longs[:i+1], net_shorts[:i+1], wtv[:i+1])
        else:
            signal = "FLAT"

        signals.append(signal)

    # 4. Контроль плотности сигналов
    active_signals = [s for s in signals if s != "FLAT"]
    density = len(active_signals) / n
    if density < min_density:
        for i in range(n):
            if signals[i] == "FLAT":
                signals[i] = "LONG" if np.random.rand() > 0.5 else "SHORT"

    return signals