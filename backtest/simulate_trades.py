import numpy as np


def simulate_trades(closes, signals, tp=0.015, sl=0.01, max_hold=10, fee=0.0005):

    balance = 1000.0
    position = None
    entry = 0.0
    entry_idx = 0

    equity_curve = []
    trades = []
    returns = []

    n = min(len(closes), len(signals))

    for i in range(n):

        price = float(closes[i])
        signal = signals[i]

        # =========================
        # ENTRY
        # =========================
        if position is None:

            if signal == "LONG":
                position = "LONG"
                entry = price
                entry_idx = i

            elif signal == "SHORT":
                position = "SHORT"
                entry = price
                entry_idx = i

        # =========================
        # LONG MANAGEMENT
        # =========================
        elif position == "LONG":

            pnl = (price - entry) / entry
            hold = i - entry_idx

            exit_trade = (
                pnl >= tp or pnl <= -sl or signal == "SHORT" or hold >= max_hold
            )

            if exit_trade:
                net = pnl - fee * 2

                balance *= 1 + net
                trades.append(net)
                returns.append(net)

                position = None

                if signal == "SHORT":
                    position = "SHORT"
                    entry = price
                    entry_idx = i

        # =========================
        # SHORT MANAGEMENT
        # =========================
        elif position == "SHORT":

            pnl = (entry - price) / entry
            hold = i - entry_idx

            exit_trade = pnl >= tp or pnl <= -sl or signal == "LONG" or hold >= max_hold

            if exit_trade:
                net = pnl - fee * 2

                balance *= 1 + net
                trades.append(net)
                returns.append(net)

                position = None

                if signal == "LONG":
                    position = "LONG"
                    entry = price
                    entry_idx = i

        equity_curve.append(balance)

    equity_curve = np.array(equity_curve)

    if len(trades) == 0:
        return {
            "final_balance": balance,
            "trades": 0,
            "winrate": 0,
            "avg_trade": 0,
            "max_drawdown": 0,
            "sharpe": 0,
            "profit_factor": 0,
        }

    peak = np.maximum.accumulate(equity_curve)
    drawdown = (equity_curve - peak) / peak

    max_dd = float(np.min(drawdown))

    returns = np.array(returns)

    sharpe = 0
    if len(returns) > 2 and np.std(returns) > 0:
        sharpe = (np.mean(returns) / (np.std(returns) + 1e-8)) * np.sqrt(252)

    winrate = np.mean(np.array(trades) > 0)

    gross_profit = np.sum([t for t in trades if t > 0])
    gross_loss = abs(np.sum([t for t in trades if t < 0])) + 1e-8

    profit_factor = gross_profit / gross_loss

    return {
        "final_balance": round(balance, 2),
        "trades": len(trades),
        "winrate": round(float(winrate), 2),
        "avg_trade": round(float(np.mean(trades)), 6),
        "max_drawdown": round(float(max_dd), 4),
        "sharpe": round(float(sharpe), 2),
        "profit_factor": round(float(profit_factor), 2),
    }
