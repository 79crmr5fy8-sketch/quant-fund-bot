import numpy as np


def simulate_trades(closes, signals):

    balance = 1000
    position = None
    entry = 0

    equity_curve = []
    trades = []
    returns = []

    for i in range(20, len(closes)):

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

            if price >= entry * 1.04 or price <= entry * 0.98:

                pnl = (price - entry) / entry
                balance *= (1 + pnl)

                trades.append(pnl)
                returns.append(pnl)

                position = None

        # EXIT SHORT
        elif position == "SHORT":

            if price <= entry * 0.96 or price >= entry * 1.02:

                pnl = (entry - price) / entry
                balance *= (1 + pnl)

                trades.append(pnl)
                returns.append(pnl)

                position = None

        equity_curve.append(balance)

    # ===========================
    # METRICS
    # ===========================

    equity_curve = np.array(equity_curve)

    # Max Drawdown
    peak = np.maximum.accumulate(equity_curve)
    drawdown = (equity_curve - peak) / peak
    max_dd = drawdown.min()

    # Sharpe (simplified)
    if len(returns) > 0:
        sharpe = np.mean(returns) / (np.std(returns) + 1e-6) * np.sqrt(252)
    else:
        sharpe = 0

    # Winrate
    winrate = len([t for t in trades if t > 0]) / len(trades) if trades else 0

    # Profit factor
    gross_profit = sum([t for t in trades if t > 0])
    gross_loss = abs(sum([t for t in trades if t < 0])) + 1e-6
    profit_factor = gross_profit / gross_loss

    return {
        "final_balance": round(balance, 2),
        "trades": len(trades),
        "winrate": round(winrate, 2),
        "avg_trade": round(np.mean(trades), 4) if trades else 0,

        # NEW METRICS
        "max_drawdown": round(max_dd, 4),
        "sharpe": round(sharpe, 2),
        "profit_factor": round(profit_factor, 2)
    }