# Corporate Finance Autopilot

##  Overview

Corporate Finance Autopilot is an AI-powered system that analyzes publicly listed companies and generates investor-style insights, financial forecasts, and strategic recommendations.

The system ingests public financial data, builds a forecasting model (Base/Upside/Downside), evaluates risk, and produces structured AI-generated reports suitable for equity or credit analysis.

---

## Architecture

Pipeline:
Ticker → Data Ingestion → Validation → Financial Modeling → Risk Engine → AI Analysis → Dashboard Output

Modules:

* Data Layer: Fetches financial data using Yahoo Finance
* Modeling Layer: Forecasts revenue scenarios
* Risk Engine: Computes risk score based on growth & volatility
* AI Layer: Generates insights, advisory, and summaries
* UI Layer: Streamlit dashboard

---

##  Tech Stack

* Python
* Streamlit
* yfinance
* pandas
* numpy
* (Optional AI: OpenAI / Ollama / local LLM)

---

## How to Run

```bash
pip install -r requirements.txt
python run.py --ticker AAPL
streamlit run app/Ui.py
```

---

## 📊 Features

* Public company data ingestion
* Financial forecasting (Base / Upside / Downside)
*  Risk scoring engine
*  AI-generated insights & advisory
*  Interactive dashboard
*  Structured investor-style report

---

##  Limitations

* Relies on publicly available financial data (Yahoo Finance)
* Some companies (e.g., pre-revenue biotech) may produce limited forecasts
* AI outputs are generated based on available data and may lack real-time updates

---

##  Data Sources

* Yahoo Finance (via yfinance)
* Public company disclosures

---

##  Future Improvements

* Multi-agent AI system with tool usage logs
* Advanced valuation models (DCF, probability-weighted biotech models)
* Better handling of pre-revenue companies
* Deployment via Docker / cloud hosting

---

## Disclaimer

This project is for educational purposes only and does not constitute financial advice.
