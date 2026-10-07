from backend.engine.risk_fusion import calculate_final_risk
from backend.engine.risk_level import get_risk_level
from backend.engine.evidence import generate_evidence
from backend.engine.recommendation import get_recommendation


def analyze_transaction(
    ml_score: float,
    graph_score: float,
    temporal_score: float,
) -> dict:
    """Combine all risk signals into a final transaction analysis."""

    # 1. Calculate final risk score
    risk_score = calculate_final_risk(
        ml_score=ml_score,
        graph_score=graph_score,
        temporal_score=temporal_score,
    )

    # 2. Convert score into risk level
    risk_level = get_risk_level(risk_score)

    # 3. Generate explainable evidence
    evidence = generate_evidence(
        ml_score=ml_score,
        graph_score=graph_score,
        temporal_score=temporal_score,
    )

    # 4. Generate recommended analyst action
    recommended_action = get_recommendation(risk_score)

    return {
        "risk_score": risk_score,
        "risk_level": risk_level,
        "evidence": evidence,
        "recommended_action": recommended_action,
    }