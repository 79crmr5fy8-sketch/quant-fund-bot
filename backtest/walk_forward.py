from backtest.engine import simulate_trades
from strategies import combined


def walk_forward(
    prices,
    net_longs,
    net_shorts,
    wtv,
    window_is=50,
    step_oos=20,
    min_density=0.25
):

    n = len(prices)
    results = []

    print(f"TOTAL DATA POINTS: {n}, window_is: {window_is}, step_oos: {step_oos}")

    if n < window_is + step_oos:
        print("NOT ENOUGH DATA")
        return []

    for start in range(0, n - window_is - step_oos, step_oos):

        end_is = start + window_is
        end_oos = end_is + step_oos

        out_sample = prices[end_is:end_oos]

        signals = combined.generate_signals(
            prices[start:end_oos],
            net_longs[start:end_oos],
            net_shorts[start:end_oos],
            wtv[start:end_oos],
            min_density=min_density
        )

        oos_signals = signals[window_is:]

        metrics = simulate_trades(out_sample, oos_signals)

        results.append({
            "strategy": "combined",
            "start": start,
            "end": end_oos,
            "metrics": metrics
        })

    return results