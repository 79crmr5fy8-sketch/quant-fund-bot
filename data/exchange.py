import ccxt

exchange = ccxt.bybit({
    "enableRateLimit": True
})


def get_ohlcv(symbol, timeframe):
    return exchange.fetch_ohlcv(symbol, timeframe, limit=60)


def get_price(symbol):
    return exchange.fetch_ticker(symbol)["last"]