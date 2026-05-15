def route_strategy(regime):

    if regime == "TRENDING_UP":
        return "TREND_FOLLOW"

    if regime == "TRENDING_DOWN":
        return "SHORT_MOMENTUM"

    if regime == "RANGE":
        return "MEAN_REVERSION"

    return "DEFENSIVE"