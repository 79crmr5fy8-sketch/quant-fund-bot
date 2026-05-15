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

# ================= RISK SETTINGS =================
BASE_RISK = 0.01
MAX_POSITIONS = 3


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


# ================= SCORING =================
def score_market(data):
    closes = [c[4] for c in data]

    momentum = (closes[-1] - closes[-5]) / closes[-5] * 100

    highs = [c[2] for c in data]
    lows = [c[3] for c in data]
    volatility = ((max(highs) - min(lows)) / closes[-1]) * 100

    score = 50

    if momentum > 0:
        score += min(momentum * 2, 25)
    else:
        score += max(momentum * 2, -25)

    if 1 < volatility < 5:
        score += 15
    elif volatility > 8:
        score -= 15

    if closes[-1] > closes[-3]:
        score += 10
    else:
        score -= 10

    return max(round(score, 2), 0)


# ================= TRADE BUILDER =================
def build_trade(symbol, signal, data, score):
    price = data[-1][4]

    # dynamic risk based on score
    if score >= 70:
        risk_mult = 1.0
    elif score >= 55:
        risk_mult = 0.6
    else:
        risk_mult = 0.0  # watch only

    if risk_mult == 0:
        return None

    size = (balance * BASE_RISK * risk_mult) / price

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
        "symbol": symbol,
        "entry": price,
        "size": size,
        "stop": stop,
        "tp1": tp1,
        "tp2": tp2,
        "tp3": tp3,
        "score": score,
        "risk_mult": risk_mult
    }


# ================= MAIN =================
def main():
    results = []

    print("\n========== MARKET SCAN v6.1 ==========")

    for symbol in symbols:
        data = get_data(symbol)

        signal = analyze(data)
        score = score_market(data)

        trade = build_trade(symbol, signal, data, score)

        # classification
        if score >= 70:
            zone = "🔥 HARD SET"
        elif score >= 55:
            zone = "🟡 SOFT SET"
        else:
            zone = "👀 WATCH"

        print(f"\n{symbol}")
        print("Signal:", signal)
        print("Score:", score)
        print("Zone:", zone)

        if trade:
            print("Trade:", trade)

        results.append((symbol, score))

    # BEST OPPORTUNITY (always shown)
    best = max(results, key=lambda x: x[1])

    print("\n========== BEST OPPORTUNITY ==========")
    print(best)


if __name__ == "__main__":
    main()