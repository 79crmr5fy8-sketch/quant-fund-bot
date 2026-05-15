from config import BALANCE, MAX_RISK


def allocate(portfolio):

    total_score = sum(p["confidence"] for p in portfolio)

    allocations = []

    used_risk = 0

    for p in sorted(portfolio, key=lambda x: x["confidence"], reverse=True):

        weight = p["confidence"] / total_score

        risk = weight * MAX_RISK

        # risk cap
        if used_risk + risk > MAX_RISK:
            continue

        used_risk += risk

        position_size = BALANCE * risk

        allocations.append({
            "symbol": p["symbol"],
            "strategy": p["strategy"],
            "confidence": p["confidence"],
            "risk": round(risk, 4),
            "position_size": round(position_size, 2)
        })

    return allocations