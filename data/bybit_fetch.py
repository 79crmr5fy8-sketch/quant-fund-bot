import ccxt
import numpy as np


def create_exchange():
    return ccxt.bybit({"enableRateLimit": True, "options": {"defaultType": "spot"}})


def fetch_ohlcv(symbol="BTC/USDT", timeframe="5m", limit=1000):
    exchange = create_exchange()

    ohlcv = exchange.fetch_ohlcv(symbol, timeframe=timeframe, limit=limit)

    closes = np.array([x[4] for x in ohlcv], dtype=float)
    highs = np.array([x[2] for x in ohlcv], dtype=float)
    lows = np.array([x[3] for x in ohlcv], dtype=float)

    return closes, highs, lows
