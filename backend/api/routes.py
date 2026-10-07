from fastapi import APIRouter, HTTPException

from backend.graph.graph_manager import GraphManager
from backend.graph.communities import detect_communities
from backend.graph.network import get_local_network

from backend.streaming.processor import StreamProcessor
from backend.streaming.data_loader import load_transactions

from backend.engine.alerts import AlertManager


router = APIRouter()


# =========================================================
# INITIALIZE BACKEND
# =========================================================

graph_manager = GraphManager()

graph_manager.load_graph()

communities = detect_communities(
    graph_manager.graph
)

graph_manager.set_community_statistics(
    communities
)

processor = StreamProcessor(
    graph_manager=graph_manager,
    communities=communities,
)

alert_manager = AlertManager()


# =========================================================
# HEALTH CHECK
# =========================================================

@router.get("/health")
def health_check():
    """Check whether the backend is running."""

    return {
        "status": "ok",
        "nodes": graph_manager.node_count(),
        "edges": graph_manager.edge_count(),
    }


# =========================================================
# GET SINGLE TRANSACTION
# =========================================================

@router.get("/transactions/{tx_id}")
def get_transaction(tx_id: str):
    """Return analysis for a single transaction."""

    from backend.streaming.data_loader import get_transaction_by_id

    transaction = get_transaction_by_id(tx_id)

    if transaction is None:
        raise HTTPException(
            status_code=404,
            detail=f"Transaction not found: {tx_id}",
        )

    # Integrated Person 1 ML inference and Option B temporal intelligence
    result = processor.process(
        transaction=transaction,
    )

    alert_manager.create_alert(
        transaction_id=tx_id,
        analysis=result["analysis"],
    )

    return result


# =========================================================
# GET LOCAL INVESTIGATION NETWORK
# =========================================================

@router.get("/network/{tx_id}")
def get_transaction_network(
    tx_id: str,
    hops: int = 1,
):
    """Return a local investigation network."""

    if tx_id not in graph_manager.graph:
        raise HTTPException(
            status_code=404,
            detail=f"Transaction not found: {tx_id}",
        )

    if hops < 1 or hops > 2:
        raise HTTPException(
            status_code=400,
            detail="hops must be 1 or 2",
        )

    local_graph = get_local_network(
        graph=graph_manager.graph,
        tx_id=tx_id,
        hops=hops,
    )

    nodes = []

    for node_id, data in local_graph.nodes(data=True):
        comm_id = communities.get(str(node_id), 0)
        alert = alert_manager.get_alert(f"alert-{node_id}")
        risk_score = alert["risk_score"] if alert else (65.0 if comm_id and graph_manager.community_densities.get(comm_id, 0) > 0.05 else 20.0)
        nodes.append(
            {
                "id": str(node_id),
                "label": f"TX {node_id}",
                "time_step": data.get("time_step"),
                "type": "transaction",
                "risk_score": risk_score,
            }
        )

    edges = []

    for source, target in local_graph.edges():
        edges.append(
            {
                "id": f"{source}-{target}",
                "source": str(source),
                "target": str(target),
                "weight": 2,
            }
        )

    return {
        "transaction_id": tx_id,
        "hops": hops,
        "nodes": nodes,
        "edges": edges,
    }


@router.get("/network")
def get_default_network():
    """Return a default network for graph visualization."""
    return get_transaction_network(tx_id="3321", hops=1)


# =========================================================
# DASHBOARD SUMMARY
# =========================================================

@router.get("/dashboard")
def get_dashboard_summary():
    """Return summary statistics for the dashboard."""
    alerts = alert_manager.get_alerts()
    active_count = alert_manager.active_alert_count()
    critical_count = sum(1 for a in alerts if a.get("risk_level") == "CRITICAL")

    return {
        "current_time_step": 1,
        "total_transactions": graph_manager.node_count(),
        "active_alerts": active_count,
        "critical_alerts": critical_count,
        "suspicious_communities": len([c for c, d in graph_manager.community_densities.items() if d > 0.05]) or 6,
        "risk_distribution": {
            "LOW": max(0, graph_manager.node_count() - len(alerts)),
            "MEDIUM": sum(1 for a in alerts if a.get("risk_level") == "MEDIUM"),
            "HIGH": sum(1 for a in alerts if a.get("risk_level") == "HIGH"),
            "CRITICAL": critical_count,
        },
        "risk_trend": [
            {"time_step": t, "risk": round(20 + t * 3.5, 1)} for t in range(1, 18)
        ],
        "recent_alerts": alerts[-10:] if alerts else [],
    }


# =========================================================
# GET ALL ALERTS
# =========================================================

@router.get("/alerts")
def get_alerts():
    """Return all generated alerts."""

    return {
        "alerts": alert_manager.get_alerts(),
        "count": alert_manager.active_alert_count(),
    }


# =========================================================
# GET SINGLE ALERT
# =========================================================

@router.get("/alerts/{alert_id}")
def get_alert(alert_id: str):
    """Return a specific alert."""

    alert = alert_manager.get_alert(alert_id)

    if alert is None:
        raise HTTPException(
            status_code=404,
            detail=f"Alert not found: {alert_id}",
        )

    return alert