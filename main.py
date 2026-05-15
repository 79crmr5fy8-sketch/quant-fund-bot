import ccxt
import time
import random

exchange = ccxt.bybit({"enableRateLimit": True})

timeframe = "15m"

symbols = ["BTC/USDT", "ETH/USDT", "SOL/USDT"]

balance = 1000

BASE_RISK = 0.01
FEE_RATE = 0.0006  # ~0.06% fee

positions = []


# ================= MARKET DATA =================
def get_price(symbol):
    return exchange.fetch_ticker(symbol)["last"]


def get_spread(symbol):
    orderbook = exchange.fetch_order_book(symbol)
    bid = orderbook["bids"][0][0]
    ask = orderbook["asks"][0][0]
    return ask - bid, bid, ask


# ================= SIGNAL =================
def analyze(price_history):
    if price_history[-1] > price_history[-2]:
        return "BUY"
    elif price_history[-1] < price_history[-2]:
        return "SELL"
    return "HOLD"


# ================= EXECUTION MODEL =================
def simulate_fill_price(symbol, side, price):
    spread, bid, ask = get_spread(symbol)

    slippage = spread * random.uniform(0.2, 1.5)

    if side == "BUY":
        return ask + slippage
    elif side == "SELL":
        return bid - slippage


# ================= FEE CALC =================
def calc_fee(notional):
    return notional * FEE_RATE


# ================= TRADE CREATION =================
def create_order(symbol, signal, price):

    size = (balance * BASE_RISK) / price

    fill_price = simulate_fill_price(symbol, signal, price)

    notional = fill_price * size
    fee = calc_fee(notional)

    if signal == "BUY":
        return {
            "symbol": symbol,
            "side": "LONG",
            "entry": fill_price,
            "size": size,
            "stop": fill_price * 0.98,
            "tp": fill_price * 1.04,
            "fee_paid": fee,
            "status": "OPEN"
        }

    if signal == "SELL":
        return {
            "symbol": symbol,
            "side": "SHORT",
            "entry": fill_price,
            "size": size,
            "stop": fill_price * 1.02,
            "tp": fill_price * 0.96,
            "fee_paid": fee,
            "status": "OPEN"
        }


# ================= POSITION ENGINE =================
def update_positions(current_prices):
    global positions

    for pos in positions:

        price = current_prices[pos["symbol"]]

        if pos["status"] != "OPEN":
            continue

        # STOP
        if pos["side"] == "LONG" and price <= pos["stop"]:
            pos["status"] = "STOPPED"
            print(f"STOP LOSS HIT {pos['symbol']}")

        if pos["side"] == "SHORT" and price >= pos["stop"]:
            pos["status"] = "STOPPED"
            print(f"STOP LOSS HIT {pos['symbol']}")

        # TAKE PROFIT
        if pos["side"] == "LONG" and price >= pos["tp"]:
            pos["status"] = "TAKE PROFIT"
            print(f"TP HIT {pos['symbol']}")

        if pos["side"] == "SHORT" and price <= pos["tp"]:
            pos["status"] = "TAKE PROFIT"
            print(f"TP HIT {pos['symbol']}")


# ================= MAIN =================
def main():

    global positions

    print("\n===== v8 EXECUTION PRO STARTED =====")

    price_history = {s: [get_price(s)] for s in symbols}

    while True:

        current_prices = {}

        # update prices
        for s in symbols:
            price = get_price(s)
            price_history[s].append(price)

            if len(price_history[s]) > 10:
                price_history[s].pop(0)

            current_prices[s] = price

        # scan opportunities
        best_trade = None
        best_score = -999

        for s in symbols:
            signal = analyze(price_history[s])
            score = random.randint(40, 90)  # placeholder scoring

            if signal == "HOLD":
                continue

            if score > best_score:
                best_score = score
                best_trade = create_order(s, signal, current_prices[s])

        # open position
        if best_trade:
            positions.append(best_trade)
            print("\nNEW EXECUTION:")
            print(best_trade)

        # manage positions
        update_positions(current_prices)

        # cleanup
        positions = [p for p in positions if p["status"] == "OPEN"]

        print(f"\nACTIVE POSITIONS: {len(positions)}")

        time.sleep(5)


if __name__ == "__main__":
    main()