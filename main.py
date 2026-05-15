import ccxt

exchange = ccxt.bybit({
    "enableRateLimit": True
})

symbol = "BTC/USDT"
timeframe = "15m"

balance = 1000
risk_per_trade = 0.01


def get_data():
    return exchange.fetch_ohlcv(symbol, timeframe, limit=10)


def analyze(data):
    closes = [c[4] for c in data]

    if closes[-1] > closes[-2]:
        return "BUY"
    elif closes[-1] < closes[-2]:
        return "SELL"
    return "HOLD"


def calculate_trade(signal, data):
    price = data[-1][4]

    risk_amount = balance * risk_per_trade
    position_size = risk_amount / price

    if signal == "BUY":
        stop = price * 0.98
        tp1 = price * 1.02
        tp2 = price * 1.04
        tp3 = price * 1.06
    elif signal == "SELL":
        stop = price * 1.02
        tp1 = price * 0.98
        tp2 = price * 0.96
        tp3 = price * 0.94
    else:
        return None

    return {
        "entry": price,
        "size": position_size,
        "stop": stop,
        "tp1": tp1,
        "tp2": tp2,
        "tp3": tp3
    }


def main():
    data = get_data()

    signal = analyze(data)

    print("Signal:", signal)

    trade = calculate_trade(signal, data)

    if trade:
        print(trade)


if __name__ == "__main__":
    main()