import numpy as np

from data.exchange import get_ohlcv
from backtest.engine import simulate_trades
from core.scoring import generate_signal


SYMBOL = "BTC/USDT"
TIMEFRAME = "15m"


def main():

    print("\n===== v9 BACKTEST + EXECUTION SYSTEM =====\n")

    ohlcv = get_ohlcv(SYMBOL, TIMEFRAME)
    closes = np.array([c[4] for c in ohlcv])

    signals = []

    # build signal series
    for i in range(len(closes)):
        if i < 20:
            signals.append("FLAT")
        else:
            window = closes[:i]
            signals.append(generate_signal(window))

    # BACKTEST
    results = simulate_trades(closes, signals)

    print("\n========== BACKTEST RESULTS ==========")
    print(results)


if __name__ == "__main__":
    main()