import numpy as np
from backtest.engine import simulate_trades
from strategies import combined

def detect_market_regime(prices, window=10, threshold=0.001):
    regimes = []
    for i in range(len(prices)):
        if i < window:
            regimes.append("flat")
            continue
        change = (prices[i] - prices[i-window]) / prices[i-window]
        regimes.append("flat" if abs(change) < threshold else "trending")
    return regimes


def walk_forward(prices, net_longs, net_shorts, wtv,
                 window_is=30, step_oos=15, min_density=0.25):

    n = len(prices)
    results = []
    print(f"TOTAL DATA POINTS: {n}, window_is: {window_is}, step_oos: {step_oos}")

    if n < window_is + step_oos:
        print("NOT ENOUGH DATA")
        return []

    regimes = detect_market_regime(prices, window=10)

    for start in range(0, n - window_is - step_oos, step_oos):
        end_is = start + window_is
        end_oos = end_is + step_oos

        in_sample = prices[start:end_is]
        out_sample = prices[end_is:end_oos]

        # Срезы для combined стратегии
        net_longs_slice = net_longs[start:end_oos]
        net_shorts_slice = net_shorts[start:end_oos]
        wtv_slice = wtv[start:end_oos]

        signals = combined.generate_signals(
            prices[start:end_oos],
            net_longs_slice,
            net_shorts_slice,
            wtv_slice,
            min_density=min_density
        )

        oos_signals = signals[window_is:]  # только out-of-sample
        metrics = simulate_trades(out_sample, oos_signals)

        results.append({
            "strategy": "combined",
            "start": start,
            "end": end_oos,
            "metrics": metrics
        })

    return results