import numpy as np


def advanced_forecast(revenue: list[float], years: int = 3) -> dict:
    revenue = np.array(revenue, dtype=float)

    if len(revenue) < 2:
        base = [float(revenue[-1])] * years
        return {
            "base": base,
            "upside": base,
            "downside": base,
            "assumptions": {
                "avg_growth": 0.0,
                "volatility": 0.0,
            },
        }

    growth_rates = []
    for i in range(1, len(revenue)):
        prev = revenue[i - 1]
        curr = revenue[i]
        if prev != 0:
            growth_rates.append((curr - prev) / prev)

    if not growth_rates:
        growth_rates = [0.0]

    avg_growth = float(np.mean(growth_rates))
    volatility = float(np.std(growth_rates))

    # clamp to keep model reasonable for demo use
    avg_growth = max(min(avg_growth, 0.25), -0.15)
    volatility = max(min(volatility, 0.12), 0.01)

    base = []
    upside = []
    downside = []

    last_base = float(revenue[-1])
    last_up = float(revenue[-1])
    last_down = float(revenue[-1])

    for _ in range(years):
        base_growth = avg_growth
        upside_growth = avg_growth + volatility
        downside_growth = avg_growth - volatility

        last_base = last_base * (1 + base_growth)
        last_up = last_up * (1 + upside_growth)
        last_down = last_down * (1 + downside_growth)

        base.append(round(last_base, 2))
        upside.append(round(last_up, 2))
        downside.append(round(last_down, 2))

    return {
        "base": base,
        "upside": upside,
        "downside": downside,
        "assumptions": {
            "avg_growth": round(avg_growth, 4),
            "volatility": round(volatility, 4),
        },
    }


def sensitivity_analysis(latest_revenue: float, growth_range: list[float]) -> list[dict]:
    results = []
    for g in growth_range:
        forecast = latest_revenue * (1 + g)
        results.append(
            {
                "growth": round(g, 4),
                "forecast": round(forecast, 2),
            }
        )
    return results