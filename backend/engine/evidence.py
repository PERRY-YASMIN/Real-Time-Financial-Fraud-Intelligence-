def generate_evidence(
    ml_score: float,
    graph_score: float,
    temporal_score: float,
) -> list[dict[str, str]]:
    """Generate human-readable evidence from risk signals."""

    evidence = []

    # ---------------------------------------------------------
    # ML evidence
    # ---------------------------------------------------------

    if ml_score >= 0.80:
        evidence.append(
            {
                "category": "ML",
                "message": "High probability of illicit activity",
            }
        )
    elif ml_score >= 0.50:
        evidence.append(
            {
                "category": "ML",
                "message": "Elevated probability of illicit activity",
            }
        )

    # ---------------------------------------------------------
    # Graph evidence
    # ---------------------------------------------------------

    if graph_score >= 0.80:
        evidence.append(
            {
                "category": "GRAPH",
                "message": "Transaction is strongly connected to suspicious network activity",
            }
        )
    elif graph_score >= 0.50:
        evidence.append(
            {
                "category": "GRAPH",
                "message": "Transaction is associated with elevated network risk",
            }
        )

    # ---------------------------------------------------------
    # Temporal evidence
    # ---------------------------------------------------------

    if temporal_score >= 0.80:
        evidence.append(
            {
                "category": "TEMPORAL",
                "message": "Activity increased sharply relative to the recent baseline",
            }
        )
    elif temporal_score >= 0.50:
        evidence.append(
            {
                "category": "TEMPORAL",
                "message": "Recent activity shows an elevated temporal risk pattern",
            }
        )

    return evidence