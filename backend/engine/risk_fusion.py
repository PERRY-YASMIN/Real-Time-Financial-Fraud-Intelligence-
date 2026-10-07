def calculate_final_risk(
    ml_score: float,
    graph_score: float,
    temporal_score: float,
) -> float:
    """Calculate the final risk score from ML, graph, and temporal signals."""

    if not 0.0 <= ml_score <= 1.0:
        raise ValueError("ml_score must be between 0 and 1")

    if not 0.0 <= graph_score <= 1.0:
        raise ValueError("graph_score must be between 0 and 1")

    if not 0.0 <= temporal_score <= 1.0:
        raise ValueError("temporal_score must be between 0 and 1")

    risk_score = 100 * (
        0.50 * ml_score
        + 0.30 * graph_score
        + 0.20 * temporal_score
    )

    return round(risk_score, 2)