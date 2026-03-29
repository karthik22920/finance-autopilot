from app.agents.ollama_client import query_ollama


# ======================
# SUMMARY
# ======================
def summarize_company(company_name, sector, industry, summary):
    prompt = f"""You are a senior equity research analyst at a top-tier investment bank.

Write a sharp, specific company summary for {company_name}.

RULES:
- Exactly 5 bullet points
- Every single bullet MUST be in normal Title Case — NEVER use ALL CAPS for any word
- Format: "- Label: sentence here."
- Never use ALL CAPS
- Each bullet is 1-2 sentences MAX
- Be specific to {company_name} — no generic filler
- Use precise language an analyst would use
- No numbering, no extra symbols, no headings outside the labels

Company: {company_name}
Sector: {sector}
Industry: {industry}

Description:
{summary}

Write the 5 bullets now:
Important: The first bullet must NOT be in all caps. Write it exactly like the others."""
    return query_ollama(prompt)


# ======================
# ANALYSIS
# ======================
def analyze_financials(data, scenarios, risk, sensitivity):
    rev = data.revenue
    ni  = data.net_income

    # Pre-compute so LLM doesn't hallucinate numbers
    rev_growth = ((rev[-1] - rev[-2]) / rev[-2] * 100) if len(rev) >= 2 and rev[-2] else 0
    ni_growth  = ((ni[-1] - ni[-2]) / ni[-2] * 100) if len(ni) >= 2 and ni[-2] else 0
    base       = scenarios.get("base", [])
    upside     = scenarios.get("upside", [])
    downside   = scenarios.get("downside", [])

    prompt = f"""You are a senior equity research analyst. Write a structured financial analysis.

USE ONLY THESE EXACT NUMBERS — do not invent or round differently:

Company: {data.company_name} ({data.sector} / {data.industry})

Revenue (most recent 4 years): {[f"${v/1e9:.1f}B" for v in rev]}
Net Income (most recent 4 years): {[f"${v/1e9:.1f}B" for v in ni]}
Revenue YoY Growth: {rev_growth:.1f}%
Net Income YoY Growth: {ni_growth:.1f}%

Forecast — Base: {[f"${v/1e9:.1f}B" for v in base]}
Forecast — Upside: {[f"${v/1e9:.1f}B" for v in upside]}
Forecast — Downside: {[f"${v/1e9:.1f}B" for v in downside]}

Risk Score: {risk.get("score", "N/A")} / 10  |  Level: {risk.get("level", "N/A")}
Risk Drivers: {", ".join(risk.get("drivers", []))}

Sensitivity: {sensitivity}

Write EXACTLY in this format — no extra sections, no bullets:

## Historical Performance
[2-3 sentences using the exact revenue and net income figures above]

## Forecast Interpretation
[2-3 sentences interpreting base/upside/downside with specific dollar figures]

## Sensitivity Interpretation
[2-3 sentences on what the sensitivity range implies for the investment thesis]

## Risk View
[2-3 sentences using the exact risk score and drivers above]

## Opportunities
[2-3 sentences on the most credible near-term opportunities for this company]"""
    return query_ollama(prompt)


# ======================
# ADVISORY
# ======================
def generate_advisory(data, analysis, risk):
    level = risk.get("level", "Unknown")
    score = risk.get("score", "N/A")
    drivers = ", ".join(risk.get("drivers", []))

    prompt = f"""You are a corporate finance advisor at a leading investment bank.

Write a balanced, professional advisory for {data.company_name}.

Context:
- Sector: {data.sector} / {data.industry}
- Risk Level: {level} (Score: {score}/10)
- Risk Drivers: {drivers}
- Analysis Summary: {analysis[:800]}

Write EXACTLY in this format — no bullets, no numbering:

## Investment Case
[2-3 sentences on the strongest argument FOR investing]

## Downside Case
[2-3 sentences on the most credible risks and what could go wrong]

## Strategic Options
[2-3 sentences on 2-3 specific, actionable strategic options for management or investors]

## Key Uncertainty
[2-3 sentences on the single biggest unknown that will determine the outcome]

## Final Recommendation
[2-3 sentences with a clear, direct recommendation — do not hedge excessively]"""
    return query_ollama(prompt)


# ======================
# INVESTMENT MEMO
# ======================
def generate_investment_memo(data, scenarios, risk, analysis, advisory):
    rev    = data.revenue
    base   = scenarios.get("base", [])
    level  = risk.get("level", "Unknown")
    score  = risk.get("score", "N/A")

    upside_delta = ""
    try:
        upside_delta = f"${(scenarios['upside'][0] - scenarios['base'][0])/1e9:.1f}B upside vs base in Year 1"
    except:
        pass

    prompt = f"""You are writing an institutional investment memo for a hedge fund portfolio committee.

This memo must be crisp, specific, and professional. No generic filler. No emojis.

Company: {data.company_name} ({data.sector})
Latest Revenue: ${rev[-1]/1e9:.1f}B
Base Forecast Y1: ${base[0]/1e9:.1f}B if base else "N/A"
Upside vs Base: {upside_delta}
Risk: {level} ({score}/10)

Key excerpts from analysis:
{analysis[:600]}

Key excerpts from advisory:
{advisory[:400]}

Write EXACTLY in this format:

## Executive View
[3-4 sentences: what this company is, why it matters now, and the core investment thesis in plain terms]

## Strengths
[3-4 sentences: the 2-3 most defensible competitive advantages backed by the financial data]

## Risks
[3-4 sentences: the 2-3 most material risks with specific reference to the risk score and drivers]

## Scenario View
[3-4 sentences: what Base, Upside, and Downside scenarios imply for returns — use specific figures]

## Conclusion
[3-4 sentences: a direct, committee-ready recommendation with key conditions or triggers to watch]"""
    return query_ollama(prompt)