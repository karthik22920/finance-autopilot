def compute_growth_rate(revenue: list[float]) -> float:
    if len(revenue) < 2 or revenue[0] == 0:
        return 0.05
    start = revenue[0]
    end = revenue[-1]
    periods = max(len(revenue) - 1, 1)
    cagr = (end / start) ** (1 / periods) - 1
    return max(min(cagr, 0.30), -0.20)


def forecast_series(last_value: float, growth: float, years: int = 3) -> list[float]:
    values = []
    current = last_value
    for _ in range(years):
        current = current * (1 + growth)
        values.append(round(current, 2))
    return values


def generate_scenarios(revenue: list[float]) -> dict:
    base_growth = compute_growth_rate(revenue)
    upside_growth = base_growth + 0.05
    downside_growth = max(base_growth - 0.05, -0.10)

    last_revenue = revenue[-1]

    return {
        "assumptions": {
            "base_growth": round(base_growth, 4),
            "upside_growth": round(upside_growth, 4),
            "downside_growth": round(downside_growth, 4),
        },
        "base": forecast_series(last_revenue, base_growth),
        "upside": forecast_series(last_revenue, upside_growth),
        "downside": forecast_series(last_revenue, downside_growth),
    }