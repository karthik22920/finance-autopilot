import argparse
import json
import os

from app.ingestion.yahoo import fetch_company_data
from app.models.financial import FinancialData
from app.forecast.advanced_model import advanced_forecast, sensitivity_analysis
from app.analysis.risk import compute_risk
from app.agents.analyzer import (
    summarize_company,
    analyze_financials,
    generate_advisory,
    generate_investment_memo
)
from app.output.report import build_report


def run_pipeline(ticker):
    ticker = ticker.upper()

    try:
        print("[Pipeline] Fetching data...")
        raw = fetch_company_data(ticker)

        print("[Pipeline] Validating...")
        data = FinancialData(**raw)

        print("[Pipeline] Forecast...")
        scenarios = advanced_forecast(data.revenue)

        print("[Pipeline] Sensitivity...")
        try:
            sensitivity = sensitivity_analysis(
                latest_revenue=data.revenue[-1],
                growth_range=[-0.05, -0.02, 0.0, 0.02, 0.05, 0.10]
            )
        except Exception:
            sensitivity = []

        print("[Pipeline] Risk...")
        try:
            risk = compute_risk(data)
        except Exception:
            risk = {"level": "Unknown", "score": 0, "drivers": []}

        print("[Pipeline] AI...")
        summary = summarize_company(
            data.company_name,
            data.sector,
            data.industry,
            data.business_summary
        )

        analysis = analyze_financials(data, scenarios, risk, sensitivity)
        advisory = generate_advisory(data, analysis, risk)
        memo = generate_investment_memo(data, scenarios, risk, analysis, advisory)

        print("[Pipeline] Report...")

        report_path = None

        try:
            report_path = build_report(
                data,
                scenarios,
                summary,
                analysis,
                advisory,
                memo,
                [],
                None,
                sensitivity,
                risk  
            )
            print(f"[Pipeline] Report created at: {report_path}")

        except Exception as e:
            print(f"[Pipeline] Report failed: {e}")
            report_path = None

        os.makedirs("data", exist_ok=True)

        dashboard = {
            "ticker": data.ticker,
            "company_name": data.company_name,
            "sector": data.sector,
            "industry": data.industry,
            "market_cap": data.market_cap,
            "currency": data.currency,
            "business_summary": data.business_summary,
            "revenue": data.revenue,
            "net_income": data.net_income,
            "scenarios": scenarios,
            "sensitivity": sensitivity,
            "risk": risk,
            "summary": summary,
            "analysis": analysis,
            "advisory": advisory,
            "investment_memo": memo,
            "report_path": report_path
        }

        with open(f"data/{ticker}_dashboard.json", "w") as f:
            json.dump(dashboard, f)

        print("[Pipeline] DONE")

    except Exception as e:
        print(f"[ERROR] {str(e)}")
        raise


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--ticker", required=True)
    args = parser.parse_args()

    run_pipeline(args.ticker)