import json
import os
import subprocess
import time
import re
import plotly.graph_objects as go
import streamlit as st

st.set_page_config(page_title="Corporate Finance Autopilot", layout="wide")

# ======================
# STYLE
# ======================
st.markdown("""
<style>
.block-container {padding-top: 1.6rem;}
</style>
""", unsafe_allow_html=True)


# ======================
# HELPERS
# ======================
def format_billions(v):
    try:
        return f"${v/1e9:.1f}B"
    except:
        return str(v)


def load_data(ticker):
    path = f"data/{ticker.upper()}_dashboard.json"
    if not os.path.exists(path):
        return None
    with open(path, "r") as f:
        return json.load(f)


def safe_growth(curr, prev):
    if prev == 0:
        return 0
    return (curr - prev) / prev


def compute_confidence(data):
    risk = data.get("risk", {})
    volatility = risk.get("avg_abs_volatility", 0)
    return round(max(0.3, min(1 - volatility, 0.95)), 2)


# ======================
# CLEAN LLM TEXT
# ======================
def clean_llm_lines(text):
    if not text:
        return []

    lines = text.split("\n")
    cleaned = []

    for line in lines:
        line = line.strip()
        if not line:
            continue
        line = re.sub(r"^\s*(?:[-•*]+|\d+[\.\)]|[A-Za-z][\.\)])\s*", "", line)
        cleaned.append(line)

    return cleaned


def render_structured(text, ordered=False):
    lines = clean_llm_lines(text)

    for i, line in enumerate(lines, start=1):
        if ordered:
            st.markdown(f"{i}. {line}")
        else:
            st.markdown(f"• {line}")


# ======================
# COMPANY HEADER
# ======================
def render_company(data):
    col1, col2 = st.columns([1.2, 1])

    with col1:
        st.title(f"{data['company_name']} ({data['ticker']})")

        short = " ".join(data["business_summary"].split(". ")[:2]) + "."
        st.write(short)

        with st.expander("📄 Full Description"):
            st.write(data["business_summary"])

    with col2:
        st.markdown("### 📌 Snapshot")
        st.write(f"**Sector:** {data['sector']}")
        st.write(f"**Industry:** {data['industry']}")
        st.write(f"**Market Cap:** {format_billions(data['market_cap'])}")
        st.write(f"**Currency:** {data['currency']}")


# ======================
# INSIGHTS
# ======================
def render_insights(data):
    revenue = data["revenue"]
    scenarios = data["scenarios"]
    risk = data["risk"]

    growth = safe_growth(revenue[-1], revenue[-2])
    upside_gap = safe_growth(scenarios["upside"][0], scenarios["base"][0])
    confidence = compute_confidence(data)

    st.markdown("## 🔍 Key Insights")

    c1, c2, c3 = st.columns(3)
    c1.info(f"📈 Growth: {growth*100:.1f}%")
    c2.success(f"🚀 Upside: {upside_gap*100:.1f}%")
    c3.warning(f"⚠️ Risk: {risk['level']}")

    st.markdown("### 💡 Strategic Signal")

    if risk["level"] == "High":
        st.error("High risk — downside exposure significant")
    elif risk["level"] == "Moderate":
        st.warning("Balanced risk-reward opportunity")
    else:
        st.success("Stable opportunity with manageable risk")

    st.caption(f"Model Confidence: {confidence}")


# ======================
# KPI
# ======================
def render_kpis(data):
    revenue = data["revenue"]
    scenarios = data["scenarios"]

    growth = safe_growth(revenue[-1], revenue[-2])

    c1, c2, c3, c4 = st.columns(4)

    c1.metric("Revenue", format_billions(revenue[-1]))
    c2.metric("Market Cap", format_billions(data["market_cap"]))
    c3.metric("Growth", f"{growth*100:.2f}%")
    c4.metric("Base Forecast", format_billions(scenarios["base"][0]))


# ======================
# RISK
# ======================
def render_risk_sensitivity(data):
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("### ⚠️ Risk Profile")
        st.metric("Level", data["risk"]["level"])
        st.metric("Score", data["risk"]["score"])

        for d in data["risk"]["drivers"]:
            st.write(f"- {d}")

    with col2:
        st.markdown("### 🧪 Sensitivity")

        for s in data["sensitivity"]:
            st.write(f"{s['growth']*100:.0f}% → {format_billions(s['forecast'])}")


# ======================
# TABLES
# ======================
def render_tables(data):
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("### 📊 Historical")
        rows = []
        for i, (r, n) in enumerate(zip(data["revenue"], data["net_income"])):
            rows.append({
                "Year": i + 1,
                "Revenue": format_billions(r),
                "Net Income": format_billions(n)
            })
        st.dataframe(rows, use_container_width=True)

    with col2:
        st.markdown("### 📉 Forecast")
        rows = []
        for i in range(len(data["scenarios"]["base"])):
            rows.append({
                "Year": f"Y{i+1}",
                "Base": format_billions(data["scenarios"]["base"][i]),
                "Upside": format_billions(data["scenarios"]["upside"][i]),
                "Downside": format_billions(data["scenarios"]["downside"][i]),
            })
        st.dataframe(rows, use_container_width=True)


# ======================
# CHARTS
# ======================
def render_charts(data):
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("### 📈 Revenue Trend")
        fig = go.Figure()
        fig.add_trace(go.Scatter(y=data["revenue"], mode="lines+markers"))
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.markdown("### 📊 Forecast")
        fig = go.Figure()
        fig.add_trace(go.Scatter(y=data["scenarios"]["base"], name="Base"))
        fig.add_trace(go.Scatter(y=data["scenarios"]["upside"], name="Upside"))
        fig.add_trace(go.Scatter(y=data["scenarios"]["downside"], name="Downside"))
        st.plotly_chart(fig, use_container_width=True)


# ======================
# AI SECTION
# ======================
def render_ai(data):
    st.markdown("## 🧠 AI Insights")

    tabs = st.tabs(["Summary", "Analysis", "Advisory", "Memo"])

    with tabs[0]:
        render_structured(data["summary"])

    with tabs[1]:
        st.markdown(data["analysis"])

    with tabs[2]:
        st.markdown(data["advisory"])

    with tabs[3]:
        st.markdown(data.get("investment_memo", ""))


# ======================
# DOWNLOAD
# ======================
def render_download(data):
    st.markdown("## 📄 Download Report")

    report_path = data.get("report_path")

    if report_path and os.path.exists(report_path):
        with open(report_path, "rb") as f:
            st.download_button(
                label="⬇️ Download Full Investment Report (PDF)",
                data=f,
                file_name=f"{data['ticker']}_report.pdf",
                mime="application/pdf",
                key="download_pdf"
            )
    else:
        st.info("Run analysis to generate report.")


# ======================
# MAIN
# ======================
st.title("📊 Corporate Finance Autopilot")

ticker = st.text_input("Ticker", "AAPL", key="ticker_input")

if st.button("Run Analysis", key="run_analysis_main"):
    progress = st.progress(0)
    status = st.empty()

    def step(p, text):
        progress.progress(p)
        status.write(text)
        time.sleep(0.4)

    step(10, "Initializing...")
    step(25, "Fetching data...")
    step(45, "Processing...")
    step(65, "Running financial model...")
    step(80, "Generating AI insights...")

    # Run pipeline
    result = subprocess.run(
        ["python", "run.py", "--ticker", ticker],
        capture_output=True,
        text=True
    )

    if result.returncode != 0:
        progress.empty()
        status.empty()
        st.error("❌ Pipeline failed")
        with st.expander("🔍 View Error Details"):
            st.code(result.stderr)
        st.stop()

    step(100, "Dashboard ready ✅")
    time.sleep(0.3)
    progress.empty()
    status.empty()

# ======================
# DASHBOARD
# ======================
data = load_data(ticker)

if data:
    render_company(data)
    st.divider()

    render_insights(data)
    st.divider()

    render_kpis(data)
    st.divider()

    render_risk_sensitivity(data)
    st.divider()

    render_tables(data)
    st.divider()

    render_charts(data)
    st.divider()

    render_ai(data)
    st.divider()

    render_download(data)