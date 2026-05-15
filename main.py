import ccxt
import numpy as np
from backtest.walk_forward import walk_forward

from strategies import combined

# ================= Настройки биржи =================
API_KEY = "ТВОЙ_API_KEY"
API_SECRET = "ТВОЙ_API_SECRET"
SYMBOL = "BTC/USDT"
TIMEFRAME = "15m"
LIMIT = 200  # свечей для анализа

# ================= Инициализация биржи =================
exchange = ccxt.bybit({
    "apiKey": API_KEY,
    "secret": API_SECRET,
    "enableRateLimit": True,
})

# ================= Получение реальных OHLCV =================
def get_real_ohlcv(symbol, timeframe, limit=100):
    """
    Возвращает массив цен закрытия
    """
    ohlcv = exchange.fetch_ohlcv(symbol, timeframe=timeframe, limit=limit)
    closes = np.array([c[4] for c in ohlcv])
    return closes

# ================= Генерация тестовых Net Positions =================
def simulate_net_positions(n):
    """
    Пример: генерируем случайные long/short объёмы
    """
    net_longs = np.random.randint(10, 100, size=n)
    net_shorts = np.random.randint(10, 100, size=n)
    return net_longs, net_shorts

# ================= Генерация WaveTrend =================
def simulate_wavetrend(prices):
    """
    Простая имитация WaveTrend как скользящая разница
    """
    wtv = np.convolve(prices, np.ones(5)/5, mode='same')  # SMA5
    return wtv

# ================= Main =================
def main():
    print("\n===== v9.6 WALK-FORWARD: Combined Strategy (Bybit) =====\n")

    closes = get_real_ohlcv(SYMBOL, TIMEFRAME, LIMIT)
    n = len(closes)
    net_longs, net_shorts = simulate_net_positions(n)
    wtv = simulate_wavetrend(closes)

    results = walk_forward(
        closes,
        net_longs=net_longs,
        net_shorts=net_shorts,
        wtv=wtv,
        window_is=30,
        step_oos=15,
        min_density=0.25
    )

    if not results:
        print("No results. Возможно, мало данных.")
        return

    # ================= Сводка по стратегиям =================
    summary = {}
    for r in results:
        s = r["strategy"]
        if s not in summary:
            summary[s] = {"final_balance": [], "winrate": [], "sharpe": [], "trades": []}
        m = r["metrics"]
        summary[s]["final_balance"].append(m["final_balance"])
        summary[s]["winrate"].append(m["winrate"])
        summary[s]["sharpe"].append(m["sharpe"])
        summary[s]["trades"].append(m["trades"])

    for s, v in summary.items():
        print(f"Strategy: {s}")
        print(f"  Avg final balance: {np.mean(v['final_balance']):.2f}")
        print(f"  Avg winrate: {np.mean(v['winrate']):.2f}")
        print(f"  Avg Sharpe: {np.mean(v['sharpe']):.2f}")
        print(f"  Avg trades: {np.mean(v['trades']):.1f}")
        print("-" * 40)

    print("\n✅ Walk-forward testing complete!")


if __name__ == "__main__":
    main()