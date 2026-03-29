from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    HRFlowable, KeepTogether
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT
from reportlab.lib.pagesizes import A4
import os

# ======================
# BRAND COLORS
# ======================
NAVY       = colors.HexColor("#0A0F2C")
ELECTRIC   = colors.HexColor("#2563EB")
ACCENT     = colors.HexColor("#F59E0B")
LIGHT_GREY = colors.HexColor("#F1F5F9")
MID_GREY   = colors.HexColor("#94A3B8")
WHITE      = colors.white
BLACK      = colors.HexColor("#0F172A")
GREEN      = colors.HexColor("#10B981")
RED        = colors.HexColor("#EF4444")

# ======================
# HELPERS
# ======================
def format_billions(v):
    try:
        return f"${v/1e9:.1f}B"
    except:
        return str(v)

def format_list(values):
    try:
        return "  ·  ".join([f"${v/1e9:.1f}B" for v in values])
    except:
        return str(values)

def clean(text):
    if not text:
        return "N/A"
    return (str(text)
            .replace("&", "&amp;")
            .replace("<", "&lt;")
            .replace(">", "&gt;")
            .replace("\n", "<br/>"))
def fix_caps(text):
    """Force-convert any ALL CAPS bullet lines to Title Case."""
    if not text:
        return text
    lines = text.split("\n")
    fixed = []
    for line in lines:
        # If line starts with "- " and is mostly uppercase, fix it
        if line.startswith("- ") and sum(1 for c in line if c.isupper()) > len(line) * 0.5:
            fixed.append("- " + line[2:].title())
        else:
            fixed.append(line)
    return "\n".join(fixed)

def get(obj, key, default="N/A"):
    try:
        if isinstance(obj, dict):
            return obj.get(key, default)
        return getattr(obj, key, default)
    except:
        return default

# ======================
# STYLES
# ======================
def make_styles():
    styles = getSampleStyleSheet()

    custom = {
        "CoverTitle": ParagraphStyle(
            "CoverTitle",
            fontName="Helvetica-Bold",
            fontSize=28,
            textColor=WHITE,
            leading=34,
            spaceAfter=6,
        ),
        "CoverSub": ParagraphStyle(
            "CoverSub",
            fontName="Helvetica",
            fontSize=13,
            textColor=colors.HexColor("#93C5FD"),
            leading=18,
            spaceAfter=4,
        ),
        "CoverMeta": ParagraphStyle(
            "CoverMeta",
            fontName="Helvetica",
            fontSize=10,
            textColor=MID_GREY,
            leading=14,
        ),
        "SectionLabel": ParagraphStyle(
            "SectionLabel",
            fontName="Helvetica-Bold",
            fontSize=8,
            textColor=ELECTRIC,
            leading=10,
            spaceBefore=2,
            letterSpacing=1.5,
        ),
        "SectionTitle": ParagraphStyle(
            "SectionTitle",
            fontName="Helvetica-Bold",
            fontSize=16,
            textColor=BLACK,
            leading=20,
            spaceBefore=2,
            spaceAfter=8,
        ),
        "Body": ParagraphStyle(
            "Body",
            fontName="Helvetica",
            fontSize=10,
            textColor=BLACK,
            leading=16,
            spaceAfter=6,
        ),
        "BodySmall": ParagraphStyle(
            "BodySmall",
            fontName="Helvetica",
            fontSize=9,
            textColor=colors.HexColor("#475569"),
            leading=14,
            spaceAfter=4,
        ),
        "Disclaimer": ParagraphStyle(
            "Disclaimer",
            fontName="Helvetica-Oblique",
            fontSize=8,
            textColor=MID_GREY,
            leading=12,
        ),
        "MetricLabel": ParagraphStyle(
            "MetricLabel",
            fontName="Helvetica",
            fontSize=8,
            textColor=MID_GREY,
            leading=10,
            alignment=TA_CENTER,
        ),
        "MetricValue": ParagraphStyle(
            "MetricValue",
            fontName="Helvetica-Bold",
            fontSize=18,
            textColor=ELECTRIC,
            leading=22,
            alignment=TA_CENTER,
        ),
        "CalloutText": ParagraphStyle(
            "CalloutText",
            fontName="Helvetica",
            fontSize=10,
            textColor=BLACK,
            leading=15,
        ),
        "TableHeader": ParagraphStyle(
            "TableHeader",
            fontName="Helvetica-Bold",
            fontSize=9,
            textColor=WHITE,
            leading=12,
            alignment=TA_CENTER,
        ),
        "TableCell": ParagraphStyle(
            "TableCell",
            fontName="Helvetica",
            fontSize=9,
            textColor=BLACK,
            leading=12,
            alignment=TA_CENTER,
        ),
    }

    return styles, custom

# ======================
# SECTION HEADER
# ======================
def section_header(label, title, custom):
    return [
        Spacer(1, 18),
        Paragraph(label.upper(), custom["SectionLabel"]),
        Paragraph(title, custom["SectionTitle"]),
        HRFlowable(width="100%", thickness=1.5, color=ELECTRIC, spaceAfter=10),
    ]

# ======================
# COVER PAGE
# ======================
def build_cover(data, custom, elements):
    ticker   = get(data, "ticker", "N/A")
    name     = get(data, "company_name", "Unknown")
    sector   = get(data, "sector", "N/A")
    industry = get(data, "industry", "N/A")
    mktcap   = format_billions(get(data, "market_cap", 0))
    currency = get(data, "currency", "USD")

    # Dark banner table
    cover_data = [[
        Paragraph(f"{name}", custom["CoverTitle"]),
    ]]
    cover_table = Table(cover_data, colWidths=[6.5*inch])
    cover_table.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,-1), NAVY),
        ("TOPPADDING",    (0,0), (-1,-1), 30),
        ("BOTTOMPADDING", (0,0), (-1,-1), 20),
        ("LEFTPADDING",   (0,0), (-1,-1), 24),
        ("RIGHTPADDING",  (0,0), (-1,-1), 24),
        ("ROUNDEDCORNERS", (0,0), (-1,-1), [8,8,8,8]),
    ]))
    elements.append(cover_table)
    elements.append(Spacer(1, 10))

    # Ticker + meta row
    meta_data = [[
        Paragraph(f"<b>{ticker}</b>", custom["CoverSub"]),
        Paragraph(f"{sector}  ·  {industry}", custom["CoverMeta"]),
        Paragraph(f"Mkt Cap: {mktcap}  ·  {currency}", custom["CoverMeta"]),
    ]]
    meta_table = Table(meta_data, colWidths=[1.2*inch, 3.2*inch, 2.1*inch])
    meta_table.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,-1), NAVY),
        ("TOPPADDING",    (0,0), (-1,-1), 10),
        ("BOTTOMPADDING", (0,0), (-1,-1), 12),
        ("LEFTPADDING",   (0,0), (-1,-1), 18),
        ("RIGHTPADDING",  (0,0), (-1,-1), 8),
        ("VALIGN", (0,0), (-1,-1), "MIDDLE"),
    ]))
    elements.append(meta_table)
    elements.append(Spacer(1, 6))
    elements.append(Paragraph(
        "⚠ AI-generated analysis using public data only. Not investment advice.",
        custom["Disclaimer"]
    ))
    elements.append(Spacer(1, 16))

# ======================
# KPI BAND
# ======================
def build_kpi_band(data, scenarios, custom, elements):
    revenue    = get(data, "revenue", [0])
    net_income = get(data, "net_income", [0])

    rev_latest = revenue[-1] if revenue else 0
    ni_latest  = net_income[-1] if net_income else 0
    growth     = ((revenue[-1] - revenue[-2]) / revenue[-2] * 100) if len(revenue) >= 2 and revenue[-2] else 0
    base_fcast = scenarios["base"][0] if scenarios.get("base") else 0

    metrics = [
        ("REVENUE", format_billions(rev_latest)),
        ("NET INCOME", format_billions(ni_latest)),
        ("YOY GROWTH", f"{growth:.1f}%"),
        ("BASE FORECAST Y1", format_billions(base_fcast)),
    ]

    cells = [[Paragraph(label, custom["MetricLabel"]), Paragraph(value, custom["MetricValue"])]
             for label, value in metrics]

    row = [Table([[c[0]], [c[1]]], colWidths=[1.5*inch]) for c in cells]
    kpi_table = Table([row], colWidths=[1.6*inch]*4)
    kpi_table.setStyle(TableStyle([
        ("BACKGROUND",    (0,0), (-1,-1), LIGHT_GREY),
        ("TOPPADDING",    (0,0), (-1,-1), 12),
        ("BOTTOMPADDING", (0,0), (-1,-1), 12),
        ("LEFTPADDING",   (0,0), (-1,-1), 6),
        ("RIGHTPADDING",  (0,0), (-1,-1), 6),
        ("ALIGN",         (0,0), (-1,-1), "CENTER"),
        ("VALIGN",        (0,0), (-1,-1), "MIDDLE"),
        ("ROUNDEDCORNERS",(0,0), (-1,-1), [6,6,6,6]),
        ("LINEAFTER",     (0,0), (2,0), 0.5, MID_GREY),
    ]))
    elements.append(kpi_table)
    elements.append(Spacer(1, 6))

# ======================
# FORECAST TABLE
# ======================
def build_forecast_table(scenarios, sensitivity, custom, elements):
    elements += section_header("Financial Model", "Forecast & Sensitivity", custom)

    # Forecast
    header = [Paragraph(h, custom["TableHeader"]) for h in ["SCENARIO", "YEAR 1", "YEAR 2", "YEAR 3"]]
    rows = [header]
    for scenario, label in [("base","Base"), ("upside","Upside"), ("downside","Downside")]:
        vals = scenarios.get(scenario, [])
        row = [Paragraph(label, custom["TableCell"])] + \
              [Paragraph(format_billions(v), custom["TableCell"]) for v in vals[:3]]
        rows.append(row)

    forecast_table = Table(rows, colWidths=[1.5*inch, 1.6*inch, 1.6*inch, 1.6*inch])
    forecast_table.setStyle(TableStyle([
        ("BACKGROUND",    (0,0), (-1,0), NAVY),
        ("BACKGROUND",    (0,1), (-1,1), LIGHT_GREY),
        ("BACKGROUND",    (0,2), (-1,2), WHITE),
        ("BACKGROUND",    (0,3), (-1,3), colors.HexColor("#FEF2F2")),
        ("TOPPADDING",    (0,0), (-1,-1), 8),
        ("BOTTOMPADDING", (0,0), (-1,-1), 8),
        ("LEFTPADDING",   (0,0), (-1,-1), 8),
        ("RIGHTPADDING",  (0,0), (-1,-1), 8),
        ("GRID",          (0,0), (-1,-1), 0.5, colors.HexColor("#E2E8F0")),
        ("ROWBACKGROUNDS",(0,1), (-1,-1), [LIGHT_GREY, WHITE, colors.HexColor("#FEF2F2")]),
    ]))
    elements.append(forecast_table)
    elements.append(Spacer(1, 12))

    # Sensitivity
    if sensitivity:
        try:
            sens_header = [Paragraph(h, custom["TableHeader"]) for h in ["GROWTH RATE", "FORECAST REVENUE"]]
            sens_rows = [sens_header]
            for s in sensitivity:
                g = int(s["growth"] * 100)
                color = GREEN if g >= 0 else RED
                sens_rows.append([
                    Paragraph(f"{g:+d}%", custom["TableCell"]),
                    Paragraph(format_billions(s["forecast"]), custom["TableCell"]),
                ])
            sens_table = Table(sens_rows, colWidths=[3.1*inch, 3.1*inch])
            sens_table.setStyle(TableStyle([
                ("BACKGROUND",    (0,0), (-1,0), ELECTRIC),
                ("TOPPADDING",    (0,0), (-1,-1), 7),
                ("BOTTOMPADDING", (0,0), (-1,-1), 7),
                ("LEFTPADDING",   (0,0), (-1,-1), 10),
                ("RIGHTPADDING",  (0,0), (-1,-1), 10),
                ("GRID",          (0,0), (-1,-1), 0.5, colors.HexColor("#E2E8F0")),
                ("ROWBACKGROUNDS",(0,1), (-1,-1), [LIGHT_GREY, WHITE]),
            ]))
            elements.append(Paragraph("SENSITIVITY ANALYSIS", custom["SectionLabel"]))
            elements.append(Spacer(1, 6))
            elements.append(sens_table)
        except:
            pass

# ======================
# RISK CALLOUT
# ======================
def build_risk(data, risk, custom, elements):
    elements += section_header("Risk Assessment", "Risk Profile", custom)

    if not risk:
        risk = get(data, "risk", {})

    if isinstance(risk, dict):
        level   = risk.get("level", "Unknown")
        score   = risk.get("score", "N/A")
        drivers = risk.get("drivers", [])
    else:
        level   = getattr(risk, "level", "Unknown")
        score   = getattr(risk, "score", "N/A")
        drivers = getattr(risk, "drivers", [])

    bg = RED if level == "High" else ACCENT if level == "Moderate" else GREEN

    risk_data = [[
        Paragraph(f"<b>RISK LEVEL</b><br/><font size=20>{level}</font>", custom["Body"]),
        Paragraph(f"<b>RISK SCORE</b><br/><font size=20>{score}</font>", custom["Body"]),
        Paragraph("<b>KEY DRIVERS</b><br/>" + "<br/>".join([f"· {d}" for d in drivers]), custom["Body"]),
    ]]
    risk_table = Table(risk_data, colWidths=[1.6*inch, 1.6*inch, 3.5*inch])
    risk_table.setStyle(TableStyle([
        ("BACKGROUND",    (0,0), (1,0), bg),
        ("BACKGROUND",    (2,0), (2,0), LIGHT_GREY),
        ("TEXTCOLOR",     (0,0), (1,0), WHITE),
        ("TOPPADDING",    (0,0), (-1,-1), 14),
        ("BOTTOMPADDING", (0,0), (-1,-1), 14),
        ("LEFTPADDING",   (0,0), (-1,-1), 12),
        ("RIGHTPADDING",  (0,0), (-1,-1), 12),
        ("VALIGN",        (0,0), (-1,-1), "MIDDLE"),
    ]))
    elements.append(risk_table)

# ======================
# AI TEXT SECTION
# ======================
def build_ai_section(label, title, content, custom, elements):
    elements += section_header(label, title, custom)

    if not content:
        elements.append(Paragraph("No data available.", custom["Body"]))
        return

    # Split on ## headings and render nicely
    parts = str(fix_caps(content)).split("##")
    for part in parts:
        part = part.strip()
        if not part:
            continue
        lines = part.split("\n", 1)
        heading = lines[0].strip()
        body    = lines[1].strip() if len(lines) > 1 else ""

        if heading:
            # Render subheading as accent pill
            pill_data = [[Paragraph(f"<b>{heading.upper()}</b>", ParagraphStyle(
                "Pill", fontName="Helvetica-Bold", fontSize=8,
                textColor=ELECTRIC, leading=10
            ))]]
            pill = Table(pill_data, colWidths=[6.5*inch])
            pill.setStyle(TableStyle([
                ("BACKGROUND",    (0,0), (-1,-1), colors.HexColor("#EFF6FF")),
                ("TOPPADDING",    (0,0), (-1,-1), 5),
                ("BOTTOMPADDING", (0,0), (-1,-1), 5),
                ("LEFTPADDING",   (0,0), (-1,-1), 10),
                ("RIGHTPADDING",  (0,0), (-1,-1), 10),
                ("LINEBELOW",     (0,0), (-1,-1), 1.5, ELECTRIC),
            ]))
            elements.append(Spacer(1, 6))
            elements.append(pill)

        if body:
            cleaned = (body.replace("&", "&amp;")
                          .replace("<", "&lt;")
                          .replace(">", "&gt;")
                          .replace("\n\n", "<br/><br/>")
                          .replace("\n", " "))
            elements.append(Spacer(1, 4))
            elements.append(Paragraph(cleaned, custom["Body"]))

# ======================
# BUILD REPORT
# ======================
def build_report(data, scenarios, summary, analysis, advisory, memo, eval_checks, chart_path, sensitivity, risk=None):
    try:
        os.makedirs("artifacts", exist_ok=True)

        ticker = get(data, "ticker", "UNKNOWN")
        path   = f"artifacts/{ticker}_report.pdf"

        doc = SimpleDocTemplate(
            path,
            pagesize=A4,
            rightMargin=0.65*inch,
            leftMargin=0.65*inch,
            topMargin=0.65*inch,
            bottomMargin=0.65*inch,
        )

        styles, custom = make_styles()
        elements = []

        # Pull risk from data if not passed directly
        if risk is None:
            risk = get(data, "risk", {})

        # --- COVER ---
        build_cover(data, custom, elements)

        # --- KPI BAND ---
        build_kpi_band(data, scenarios, custom, elements)

        # --- COMPANY OVERVIEW ---
        elements += section_header("Company", "Business Overview", custom)
        biz = get(data, "business_summary", "No description available.")
        elements.append(Paragraph(clean(biz), custom["Body"]))

        # --- FINANCIALS ---
        elements += section_header("Financials", "Historical Performance", custom)
        revenue    = get(data, "revenue", [])
        net_income = get(data, "net_income", [])

        fin_header = [Paragraph(h, custom["TableHeader"]) for h in ["PERIOD", "REVENUE", "NET INCOME"]]
        fin_rows   = [fin_header]
        for i, (r, n) in enumerate(zip(revenue, net_income)):
            fin_rows.append([
                Paragraph(f"Year {i+1}", custom["TableCell"]),
                Paragraph(format_billions(r), custom["TableCell"]),
                Paragraph(format_billions(n), custom["TableCell"]),
            ])
        fin_table = Table(fin_rows, colWidths=[2.1*inch, 2.2*inch, 2.2*inch])
        fin_table.setStyle(TableStyle([
            ("BACKGROUND",    (0,0), (-1,0), NAVY),
            ("TOPPADDING",    (0,0), (-1,-1), 8),
            ("BOTTOMPADDING", (0,0), (-1,-1), 8),
            ("LEFTPADDING",   (0,0), (-1,-1), 10),
            ("RIGHTPADDING",  (0,0), (-1,-1), 10),
            ("GRID",          (0,0), (-1,-1), 0.5, colors.HexColor("#E2E8F0")),
            ("ROWBACKGROUNDS",(0,1), (-1,-1), [LIGHT_GREY, WHITE]),
        ]))
        elements.append(fin_table)

        # --- FORECAST + SENSITIVITY ---
        build_forecast_table(scenarios, sensitivity, custom, elements)

        # --- RISK ---
        build_risk(data, risk, custom, elements)

        # --- AI SECTIONS ---
        build_ai_section("AI Research", "Company Summary", summary, custom, elements)
        build_ai_section("AI Research", "Financial Analysis", analysis, custom, elements)
        build_ai_section("Advisory", "Strategic Advisory", advisory, custom, elements)
        build_ai_section("Investment Memo", "Investment Memo", memo, custom, elements)

        # --- FOOTER DISCLAIMER ---
        elements.append(Spacer(1, 24))
        elements.append(HRFlowable(width="100%", thickness=0.5, color=MID_GREY))
        elements.append(Spacer(1, 6))
        elements.append(Paragraph(
            "This report was generated by Corporate Finance Autopilot using publicly available data and AI-generated analysis. "
            "It does not constitute financial advice. Past performance is not indicative of future results. "
            "Always consult a qualified financial advisor before making investment decisions.",
            custom["Disclaimer"]
        ))

        doc.build(elements)
        print(f"[Report] ✅ PDF saved: {path}")
        return path

    except Exception as e:
        print(f"[Report] ❌ ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        return None