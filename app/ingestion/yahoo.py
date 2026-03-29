import yfinance as yf


class InvalidTickerError(Exception):
    """Raised when a ticker is invalid or has no usable financial data."""
    pass


def fetch_company_data(ticker: str) -> dict:
    ticker = ticker.strip().upper()

    if not ticker or not ticker.isalpha() or len(ticker) > 10:
        raise InvalidTickerError(f"'{ticker}' is not a valid ticker format.")

    ticker_obj = yf.Ticker(ticker)
    info = ticker_obj.info

    # Detect invalid / delisted ticker — yfinance returns minimal info
    company_name = info.get("longName") or info.get("shortName")
    if not company_name:
        raise InvalidTickerError(
            f"Ticker '{ticker}' not found. It may be invalid, delisted, or unsupported."
        )

    # ----------------------------
    # Financials
    # ----------------------------
    financials = ticker_obj.financials

    revenue = []
    net_income = []

    if financials is not None and not financials.empty:
        if "Total Revenue" in financials.index:
            revenue = list(financials.loc["Total Revenue"].dropna())
        if "Net Income" in financials.index:
            net_income = list(financials.loc["Net Income"].dropna())

    # Reverse to chronological order (old → new)
    revenue = revenue[::-1]
    net_income = net_income[::-1]

    if not revenue:
        raise InvalidTickerError(
            f"No financial data found for '{ticker}'. "
            "This may be a non-public company, ETF, or crypto ticker."
        )

    # ----------------------------
    # Price Data
    # ----------------------------
    hist = ticker_obj.history(period="5y")

    prices = []
    if hist is not None and not hist.empty:
        prices = hist["Close"].dropna().tolist()

    # ----------------------------
    # Growth Calculation
    # ----------------------------
    if len(revenue) >= 2 and revenue[-2] != 0:
        growth = (revenue[-1] - revenue[-2]) / revenue[-2]
    else:
        growth = 0

    # ----------------------------
    # Upside Placeholder
    # ----------------------------
    upside = 0.02

    # ----------------------------
    # Final Payload
    # ----------------------------
    payload = {
        "ticker": ticker,
        "company_name": company_name,
        "sector": info.get("sector", "Unknown"),
        "industry": info.get("industry", "Unknown"),
        "website": info.get("website", ""),
        "business_summary": info.get(
            "longBusinessSummary",
            "Public company with limited summary available."
        ),
        "market_cap": float(info["marketCap"]) if info.get("marketCap") else 0.0,
        "currency": info.get("currency", "USD"),
        "revenue": revenue,
        "net_income": net_income,
        "prices": prices,
        "growth": growth,
        "upside": upside,
    }

    return payload