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
        nodes.append(
            {
                "id": node_id,
                "label": node_id,
                "time_step": data.get("time_step"),
                "type": "transaction",
            }
        )

    edges = []

    for source, target in local_graph.edges():
        edges.append(
            {
                "id": f"{source}-{target}",
                "source": source,
                "target": target,
            }
        )

    return {
        "transaction_id": tx_id,
        "hops": hops,
        "nodes": nodes,
        "edges": edges,
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