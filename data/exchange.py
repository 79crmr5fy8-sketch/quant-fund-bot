import random
import time

def get_ohlcv(symbol, timeframe, limit=100):
    """
    Фейковые данные OHLCV для тестирования.
    Возвращает список [timestamp, open, high, low, close, volume]
    """
    ohlcv = []
    base_price = 1000.0
    ts = int(time.time())

    for i in range(limit):
        o = base_price + random.uniform(-5, 5)
        h = o + random.uniform(0, 5)
        l = o - random.uniform(0, 5)
        c = o + random.uniform(-3, 3)
        v = random.uniform(1, 10)
        ohlcv.append([ts + i * 60, o, h, l, c, v])
        base_price = c
    return ohlcv