import ccxt

exchange = ccxt.bybit({
    "enableRateLimit": True
})

timeframe = "15m"

symbols = [
    "BTC/USDT",
    "ETH/USDT",
    "SOL/USDT",
    "XRP/USDT",
    "DOGE/USDT"
]

balance = 1000
risk_per_trade = 0.01


# ================= DATA =================
def get_data(symbol):
    return exchange.fetch_ohlcv(symbol, timeframe, limit=20)


# ================= SIGNAL =================
def analyze(data):
    closes = [c[4] for c in data]

    if closes[-1] > closes[-2]:
        return "BUY"
    elif closes[-1] < closes[-2]:
        return "SELL"
    return "HOLD"


# ================= SCORING ENGINE =================
def score_market(data):
    closes = [c[4] for c in data]

    # momentum
    momentum = (closes[-1] - closes[-5]) / closes[-5] * 100

    # volatility
    highs = [c[2] for c in data]
    lows = [c[3] for c in data]
    volatility = ((max(highs) - min(lows)) / closes[-1]) * 100

    score = 50  # base score

    # momentum contribution
    if momentum > 0:
        score += min(momentum * 2, 25)
    else:
        score += max(momentum * 2, -25)

    # volatility adjustment
    if 1 < volatility < 5:
        score += 15
    elif volatility > 8:
        score -= 15

    # trend bias
    if closes[-1] > closes[-3]:
        score += 10
    else:
        score -= 10

    return round(score, 2)


# ================= TRADE PLAN =================
def calculate_trade(signal, data):
    price = data[-1][4]

    risk_amount = balance * risk_per_trade
    size = risk_amount / price

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
        "size": size,
        "stop": stop,
        "tp1": tp1,
        "tp2": tp2,
        "tp3": tp3
    }


# ================= MAIN LOOP =================
def main():
    results = []

    for symbol in symbols:
        data = get_data(symbol)

        signal = analyze(data)
        score = score_market(data)

        trade = calculate_trade(signal, data)

        print(f"\n{symbol}")
        print("Signal:", signal)
        print("Score:", score)

        if trade:
            print("Trade:", trade)

        results.append((symbol, signal, score))

    # BEST TRADE SELECTION
    best = max(results, key=lambda x: x[2])

    print("\n======================")
    print("BEST SETUP:")
    print(best)


if __name__ == "__main__":
    main()