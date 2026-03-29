import os
import matplotlib.pyplot as plt


def plot_revenue_forecast(history: list[float], scenarios: dict, ticker: str) -> str:
    os.makedirs("artifacts", exist_ok=True)

    hist_x = list(range(1, len(history) + 1))
    base_x = list(range(len(history), len(history) + len(scenarios["base"]) + 1))

    base_y = [history[-1]] + scenarios["base"]
    up_y = [history[-1]] + scenarios["upside"]
    down_y = [history[-1]] + scenarios["downside"]

    plt.figure(figsize=(10, 6))

    plt.plot(hist_x, history, label="Historical Revenue")
    plt.plot(base_x, base_y, label="Base Case")
    plt.plot(base_x, up_y, label="Upside Case")
    plt.plot(base_x, down_y, label="Downside Case")

    plt.title(f"{ticker} Revenue Forecast (Base / Upside / Downside Scenarios)")
    plt.xlabel("Year Index")
    plt.ylabel("Revenue")
    plt.legend()

    output_path = f"artifacts/{ticker}_forecast.png"
    plt.tight_layout()
    plt.savefig(output_path)
    plt.close()

    return output_path