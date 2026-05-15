import ccxt
import numpy as np

exchange = ccxt.bybit({"enableRateLimit": True})

symbols = ["BTC/USDT", "ETH/USDT", "SOL/USDT", "XRP/USDT", "DOGE/USDT"]

timeframe = "15m"


# ================= DATA =================
def get_ohlcv(symbol):
    return exchange.fetch_ohlcv(symbol, timeframe, limit=60)


# ================= REGIME =================
def detect_regime(closes):
    returns = np.diff(closes)
    volatility = np.std(returns)
    trend = (closes[-1] - closes[-20]) / closes[-20]

    vol_threshold = np.std(closes) * 0.02

    if volatility > vol_threshold * 3:
        return "VOLATILE"

    if abs(trend) < 0.02:
        return "RANGE"

    if trend > 0:
        return "TRENDING_UP"

    return "TRENDING_DOWN"


# ================= SETUP TYPE =================
def classify_setup(closes, regime):
    momentum = (closes[-1] - closes[-10]) / closes[-10]

    if regime == "RANGE":
        return "MEAN_REVERSION"

    if regime == "TRENDING_UP":
        return "CONTINUATION" if momentum > 0 else "PULLBACK"

    if regime == "TRENDING_DOWN":
        return "CONTINUATION" if momentum < 0 else "PULLBACK"

    return "NOISE"


# ================= FEATURES =================
def features(closes):
    trend = (np.mean(closes[-5:]) - np.mean(closes[-20:])) / np.mean(closes[-20:])
    momentum = (closes[-1] - closes[-10]) / closes[-10]

    return trend, momentum


# ================= CONFIDENCE =================
def compute_confidence(trend, momentum, regime, setup):
    score = (
        abs(trend) * 120 +
        abs(momentum) * 80
    )

    # regime bias
    if regime == "TRENDING_UP" and setup == "CONTINUATION":
        score *= 1.2

    if regime == "RANGE" and setup == "MEAN_REVERSION":
        score *= 1.15

    if regime == "VOLATILE":
        score *= 0.7

    return max(min(score, 100), 0)


# ================= ENGINE =================
def analyze(symbol):
    ohlcv = get_ohlcv(symbol)
    closes = np.array([c[4] for c in ohlcv])

    regime = detect_regime(closes)
    setup = classify_setup(closes, regime)

    trend, momentum = features(closes)

    confidence = compute_confidence(trend, momentum, regime, setup)

    return {
        "symbol": symbol,
        "regime": regime,
        "setup": setup,
        "trend": round(trend, 4),
        "momentum": round(momentum, 4),
        "confidence": round(confidence, 2)
    }


# ================= MAIN =================
def main():

    print("\n===== v8.3 ALWAYS-ON RANKING SYSTEM =====\n")

    results = []

    for s in symbols:
        r = analyze(s)
        results.append(r)

        print(f"{s}")
        print(r)
        print("-" * 40)

    # ALWAYS SORT (core idea)
    results.sort(key=lambda x: x["confidence"], reverse=True)

    print("\n========== TOP SETUPS ==========")

    top_n = 3

    for i, r in enumerate(results[:top_n]):
        print(f"\n#{i+1} {r['symbol']}")
        print(f"confidence: {r['confidence']}")
        print(f"regime: {r['regime']}")
        print(f"setup: {r['setup']}")

    print("\nBEST TRADE IDEA:")
    print(results[0])


if __name__ == "__main__":
    main()