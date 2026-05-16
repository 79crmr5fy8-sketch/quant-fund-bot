from strategies.combined import generate_signals
from backtest.simulate_trades import simulate_trades


def walk_forward(prices, net_longs, net_shorts, wtv, window=100, step=30):

    results = []

    for start in range(0, len(prices) - window, step):

        end = start + window

        closes = prices[start:end]
        longs = net_longs[start:end]
        shorts = net_shorts[start:end]
        wave = wtv[start:end]

        signals = generate_signals(closes, longs, shorts, wave)

        res = simulate_trades(closes, signals)

        results.append(res)

    return results
