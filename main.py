import ccxt
import time

exchange = ccxt.bybit({"enableRateLimit": True})

timeframe = "15m"

symbols = ["BTC/USDT", "ETH/USDT", "SOL/USDT"]

balance = 1000

BASE_RISK = 0.01

# ================= ACTIVE POSITION STORAGE =================
positions = []


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


# ================= SCORE =================
def score_market(data):
    closes = [c[4] for c in data]

    momentum = (closes[-1] - closes[-5]) / closes[-5] * 100

    score = 50 + momentum * 2

    return max(min(score, 100), 0)


# ================= TRADE CREATION =================
def create_trade(symbol, signal, data, score):
    price = data[-1][4]

    size = (balance * BASE_RISK) / price

    if signal == "HOLD" or score < 55:
        return None

    if signal == "BUY":
        return {
            "symbol": symbol,
            "side": "LONG",
            "entry": price,
            "size": size,
            "tp1": price * 1.02,
            "tp2": price * 1.04,
            "tp3": price * 1.06,
            "stop": price * 0.98,
            "status": "OPEN",
            "tp1_hit": False,
            "tp2_hit": False,
            "tp3_hit": False
        }

    if signal == "SELL":
        return {
            "symbol": symbol,
            "side": "SHORT",
            "entry": price,
            "size": size,
            "tp1": price * 0.98,
            "tp2": price * 0.96,
            "tp3": price * 0.94,
            "stop": price * 1.02,
            "status": "OPEN",
            "tp1_hit": False,
            "tp2_hit": False,
            "tp3_hit": False
        }


# ================= POSITION MANAGEMENT =================
def update_positions(current_price):
    global positions

    for pos in positions:

        if pos["status"] != "OPEN":
            continue

        # TP1
        if not pos["tp1_hit"]:
            if (pos["side"] == "LONG" and current_price >= pos["tp1"]) or \
               (pos["side"] == "SHORT" and current_price <= pos["tp1"]):
                pos["tp1_hit"] = True
                print(f"TP1 hit: {pos['symbol']}")

        # TP2
        if pos["tp1_hit"] and not pos["tp2_hit"]:
            if (pos["side"] == "LONG" and current_price >= pos["tp2"]) or \
               (pos["side"] == "SHORT" and current_price <= pos["tp2"]):
                pos["tp2_hit"] = True
                print(f"TP2 hit: {pos['symbol']} → move stop to BE")

                # breakeven
                pos["stop"] = pos["entry"]

        # TP3 (close)
        if pos["tp2_hit"] and not pos["tp3_hit"]:
            if (pos["side"] == "LONG" and current_price >= pos["tp3"]) or \
               (pos["side"] == "SHORT" and current_price <= pos["tp3"]):
                pos["tp3_hit"] = True
                pos["status"] = "CLOSED"
                print(f"TP3 hit: CLOSE {pos['symbol']}")


# ================= MAIN LOOP =================
def main():

    global positions

    print("\n===== EXECUTION INTELLIGENCE v7 STARTED =====")

    while True:

        best_trade = None
        best_score = 0

        # scan market
        for symbol in symbols:

            data = get_data(symbol)

            signal = analyze(data)
            score = score_market(data)

            trade = create_trade(symbol, signal, data, score)

            if trade and score > best_score:
                best_score = score
                best_trade = trade

        # open new position
        if best_trade:
            positions.append(best_trade)
            print("\nNEW POSITION OPENED:")
            print(best_trade)

        # update existing positions
        if positions:
            current_price = exchange.fetch_ticker(symbols[0])["last"]
            update_positions(current_price)

        # clean closed positions
        positions = [p for p in positions if p["status"] != "CLOSED"]

        print(f"\nACTIVE POSITIONS: {len(positions)}")
        time.sleep(10)


if __name__ == "__main__":
    main()