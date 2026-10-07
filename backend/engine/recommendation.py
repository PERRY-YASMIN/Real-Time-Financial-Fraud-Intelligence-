def get_recommendation(risk_score: float) -> str:
    """Return the recommended analyst action for a risk score."""

    if not 0 <= risk_score <= 100:
        raise ValueError("risk_score must be between 0 and 100")

    if risk_score >= 80:
        return "INVESTIGATE"

    if risk_score >= 60:
        return "REVIEW"

    if risk_score >= 30:
        return "MONITOR"

    return "NO_ACTION"