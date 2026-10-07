def get_risk_level(risk_score: float) -> str:
    """Convert a 0-100 risk score into a risk level."""

    if not 0 <= risk_score <= 100:
        raise ValueError("risk_score must be between 0 and 100")

    if risk_score < 30:
        return "LOW"

    if risk_score < 60:
        return "MEDIUM"

    if risk_score < 80:
        return "HIGH"

    return "CRITICAL"