import numpy as np


def simulate_trades(closes, signals, tp=0.02, sl=0.01, max_hold=5, fee=0.0006):

    balance = 1000.0

    position = None
    entry = 0.0
    entry_idx = 0

    equity_curve = []
    trades = []
    returns = []

    n = min(len(closes), len(signals))

    for i in range(n):

        price = closes[i]
        signal = signals[i]

        if position is None:

            if signal in ["LONG", "SHORT"]:
                position = signal
                entry = price
                entry_idx = i

        elif position == "LONG":

            pnl = (price - entry) / entry
            bars = i - entry_idx

            if pnl >= tp or pnl <= -sl or signal == "SHORT" or bars >= max_hold:

                net = pnl - fee * 2
                balance *= 1 + net
                trades.append(net)
                returns.append(net)

                position = None

        elif position == "SHORT":

            pnl = (entry - price) / entry
            bars = i - entry_idx

            if pnl >= tp or pnl <= -sl or signal == "LONG" or bars >= max_hold:

                net = pnl - fee * 2
                balance *= 1 + net
                trades.append(net)
                returns.append(net)

                position = None

        equity_curve.append(balance)

    equity_curve = np.array(equity_curve)

    if len(equity_curve) == 0:
        return {"final_balance": 1000, "trades": 0, "winrate": 0, "sharpe": 0}

    peak = np.maximum.accumulate(equity_curve)
    dd = (equity_curve - peak) / peak

    sharpe = (
        (np.mean(returns) / (np.std(returns) + 1e-8)) * np.sqrt(252)
        if len(returns) > 1
        else 0
    )
    winrate = len([t for t in trades if t > 0]) / len(trades) if trades else 0

    return {
        "final_balance": round(balance, 2),
        "trades": len(trades),
        "winrate": round(winrate, 2),
        "sharpe": round(sharpe, 2),
        "max_drawdown": round(float(dd.min()) if len(dd) else 0, 4),
    }
