import numpy as np


def sigmoid(x):
    return 1 / (1 + np.exp(-x))


def zscore(x):
    return (x - np.mean(x)) / (np.std(x) + 1e-8)
