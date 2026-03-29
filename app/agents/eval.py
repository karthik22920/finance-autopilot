def validate_output(text: str) -> list[str]:
    checks = []
    lower = text.lower()

    if "risk" in lower:
        checks.append("PASS: risk discussion present")
    else:
        checks.append("WARN: missing explicit risk discussion")

    if "uncert" in lower:
        checks.append("PASS: uncertainty acknowledged")
    else:
        checks.append("WARN: uncertainty not clearly labeled")

    if "recommend" in lower or "investment case" in lower:
        checks.append("PASS: recommendation present")
    else:
        checks.append("WARN: recommendation may be incomplete")

    return checks