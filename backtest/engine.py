import numpy as np


def simulate_trades(closes, signals):

    balance = 1000.0
    position = None
    entry = 0.0

    equity_curve = []
    trades = []
    returns = []

    n = min(len(closes), len(signals))

    for i in range(n):

        price = closes[i]
        signal = signals[i]

        # ENTRY
        if position is None:

            if signal == "LONG":
                position = "LONG"
                entry = price

            elif signal == "SHORT":
                position = "SHORT"
                entry = price

        # EXIT LONG
        elif position == "LONG":
            if price >= entry * 1.01 or price <= entry * 0.99:
                pnl = (price - entry) / entry
                balance *= (1 + pnl)
                trades.append(pnl)
                returns.append(pnl)
                position = None

        # EXIT SHORT
        elif position == "SHORT":
            if price <= entry * 0.99 or price >= entry * 1.01:
                pnl = (entry - price) / entry
                balance *= (1 + pnl)
                trades.append(pnl)
                returns.append(pnl)
                position = None

        equity_curve.append(balance)

    equity_curve = np.array(equity_curve)

    if len(equity_curve) == 0:
        return {
            "final_balance": 1000,
            "trades": 0,
            "winrate": 0,
            "avg_trade": 0,
            "max_drawdown": 0,
            "sharpe": 0,
            "profit_factor": 0
        }

    peak = np.maximum.accumulate(equity_curve)
    drawdown = (equity_curve - peak) / peak
    max_dd = float(drawdown.min()) if len(drawdown) > 0 else 0

    if len(returns) > 1:
        sharpe = np.mean(returns) / (np.std(returns) + 1e-8) * np.sqrt(252)
    else:
        sharpe = 0

    winrate = len([t for t in trades if t > 0]) / len(trades) if trades else 0

    gross_profit = sum([t for t in trades if t > 0])
    gross_loss = abs(sum([t for t in trades if t < 0])) + 1e-8

    profit_factor = gross_profit / gross_loss if trades else 0

    return {
        "final_balance": round(balance, 2),
        "trades": len(trades),
        "winrate": round(winrate, 2),
        "avg_trade": round(np.mean(trades), 4) if trades else 0,
        "max_drawdown": round(max_dd, 4),
        "sharpe": round(sharpe, 2),
        "profit_factor": round(profit_factor, 2)
    }