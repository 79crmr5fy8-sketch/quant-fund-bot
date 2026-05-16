from backtest.walk_forward import walk_forward
import numpy as np


def main():

    print("===== v10.7 WALK-FORWARD =====")

    # fake data placeholder (replace with Bybit fetch)
    prices = np.random.normal(100, 1, 500).cumsum()

    net_longs = np.random.randint(40, 100, 500)
    net_shorts = np.random.randint(40, 100, 500)

    wtv = np.random.rand(500) * 100

    results = walk_forward(prices, net_longs, net_shorts, wtv)

    print("DONE")
    print(results)


if __name__ == "__main__":
    main()
