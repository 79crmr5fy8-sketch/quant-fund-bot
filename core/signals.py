import numpy as np

def extract_features(closes):

    return {
        "trend": (np.mean(closes[-5:]) - np.mean(closes[-20:])) / np.mean(closes[-20:]),
        "momentum": (closes[-1] - closes[-10]) / closes[-10]
    }