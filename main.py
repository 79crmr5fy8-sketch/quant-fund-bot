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
BASE_RISK = 0.01          # 1% per trade
MAX_POSITIONS = 3         # max open trades
MIN_SCORE = 60            # ignore weak signals
MAX_PORTFOLIO_RISK = 0.03 # max 3% total risk


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
        score -= 20

    if closes[-1] > closes[-3]:
        score += 10
    else:
        score -= 10

    return max(round(score, 2), 0)


# ================= TRADE BUILDER =================
def build_trade(symbol, signal, data, allocation, risk_factor):
    price = data[-1][4]

    size = (balance * allocation * risk_factor) / price

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
        "risk": risk_factor
    }


# ================= RISK ENGINE =================
def risk_adjustment(avg_score):
    """
    worse market → reduce risk
    strong market → increase risk slightly
    """
    if avg_score > 80:
        return 1.2
    elif avg_score > 60:
        return 1.0
    elif avg_score > 50:
        return 0.7
    else:
        return 0.4


# ================= MAIN =================
def main():
    results = []

    # 1. scan market
    for symbol in symbols:
        data = get_data(symbol)

        signal = analyze(data)
        score = score_market(data)

        results.append({
            "symbol": symbol,
            "signal": signal,
            "score": score,
            "data": data
        })

    # 2. filter weak signals
    filtered = [
        r for r in results
        if r["signal"] != "HOLD" and r["score"] >= MIN_SCORE
    ]

    if not filtered:
        print("No valid setups")
        return

    # 3. sort by strength
    filtered.sort(key=lambda x: x["score"], reverse=True)

    # 4. limit positions
    filtered = filtered[:MAX_POSITIONS]

    # 5. compute avg score
    avg_score = sum(r["score"] for r in filtered) / len(filtered)

    # 6. dynamic risk
    risk_factor = risk_adjustment(avg_score)

    print("\n================ PORTFOLIO (v6 RISK CONTROL) ================")
    print(f"Avg score: {avg_score}")
    print(f"Risk factor: {risk_factor}")
    print(f"Positions allowed: {len(filtered)}")

    portfolio_risk = 0

    portfolio = []

    # 7. allocate capital safely
    total_score = sum(r["score"] for r in filtered)

    for r in filtered:
        allocation = r["score"] / total_score

        trade = build_trade(
            r["symbol"],
            r["signal"],
            r["data"],
            allocation,
            risk_factor
        )

        portfolio_risk += allocation * BASE_RISK

        # 8. enforce global risk cap
        if portfolio_risk > MAX_PORTFOLIO_RISK:
            print(f"SKIP {r['symbol']} → risk limit reached")
            continue

        portfolio.append(trade)

        print(f"\n{r['symbol']}")
        print("Signal:", r["signal"])
        print("Score:", r["score"])
        print("Allocation:", round(allocation * 100, 2), "%")
        print("Trade:", trade)

    print("\n================ SUMMARY ================")
    print(f"Final positions: {len(portfolio)}")
    print(f"Total portfolio risk: {round(portfolio_risk * 100, 2)}%")


if __name__ == "__main__":
    main()