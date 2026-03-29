# ================================
# Risk Engine (Pydantic Compatible)
# ================================

def compute_risk(data) -> dict:
    revenue = data.revenue

    if len(revenue) < 2:
        return {
            "score": 1,
            "level": "Low",
            "drivers": ["Insufficient revenue history"],
            "avg_abs_volatility": 0,
        }

    # ----------------------------
    # Revenue Volatility
    # ----------------------------
    changes = []
    for i in range(1, len(revenue)):
        prev = revenue[i - 1]
        curr = revenue[i]
        if prev != 0:
            changes.append((curr - prev) / prev)

    avg_abs_volatility = (
        sum(abs(x) for x in changes) / len(changes)
        if changes else 0
    )

    risk_score = 0
    drivers = []

    if avg_abs_volatility > 0.08:
        risk_score += 2
        drivers.append("Revenue volatility elevated")
    else:
        risk_score += 1
        drivers.append("Revenue relatively stable")

    # ----------------------------
    # Growth Risk
    # ----------------------------
    growth = getattr(data, "growth", 0)

    if growth < 0.05:
        risk_score += 2
        drivers.append("Low growth momentum")
    elif growth < 0.10:
        risk_score += 1
        drivers.append("Moderate growth")

    # ----------------------------
    # Upside Risk
    # ----------------------------
    upside = getattr(data, "upside", 0)

    if upside < 0.03:
        risk_score += 2
        drivers.append("Limited upside potential")
    elif upside < 0.07:
        risk_score += 1
        drivers.append("Moderate upside potential")

    # ----------------------------
    # Size Factor
    # ----------------------------
    market_cap = data.market_cap

    if market_cap > 1e11:
        drivers.append("Large-cap stability supports resilience")
    else:
        risk_score += 1
        drivers.append("Smaller scale may reduce resilience")

    # ----------------------------
    # Final Classification
    # ----------------------------
    if risk_score >= 5:
        level = "High"
    elif risk_score >= 3:
        level = "Moderate"
    else:
        level = "Low"

    return {
        "score": risk_score,
        "level": level,
        "drivers": drivers,
        "avg_abs_volatility": round(avg_abs_volatility, 4),
    }