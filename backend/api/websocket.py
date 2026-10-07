import asyncio

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from backend.engine.alerts import AlertManager
from backend.graph.communities import detect_communities
from backend.graph.graph_manager import GraphManager
from backend.streaming.data_loader import load_transactions
from backend.streaming.processor import StreamProcessor


router = APIRouter()


# =========================================================
# INITIALIZE BACKEND COMPONENTS
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
# WEBSOCKET STREAM
# =========================================================

@router.websocket("/ws/stream")
async def stream_transactions(websocket: WebSocket):
    """Stream transactions with real-time risk analysis."""

    await websocket.accept()

    transactions = load_transactions()

    try:
        for transaction in transactions:

            # -------------------------------------------------
            # Temporary ML + temporal values
            # -------------------------------------------------
            #
            # Person 1's pipeline will eventually provide these.
            #

            ml_score = 0.87
            temporal_score = 0.72

            # -------------------------------------------------
            # Analyze transaction
            # -------------------------------------------------

            result = processor.process(
                transaction=transaction,
                ml_score=ml_score,
                temporal_score=temporal_score,
            )

            analysis = result["analysis"]

            # -------------------------------------------------
            # Generate alert if necessary
            # -------------------------------------------------

            alert = alert_manager.create_alert(
                transaction_id=transaction.tx_id,
                analysis=analysis,
            )

            # -------------------------------------------------
            # Send transaction event
            # -------------------------------------------------

            event = {
                "type": "transaction",
                "transaction": {
                    "id": transaction.tx_id,
                    "time_step": transaction.time_step,
                },
                "analysis": analysis,
            }

            await websocket.send_json(event)

            # -------------------------------------------------
            # Send alert event
            # -------------------------------------------------

            if alert is not None:

                alert_event = {
                    "type": "alert",
                    "alert": alert,
                }

                await websocket.send_json(
                    alert_event
                )

            # -------------------------------------------------
            # Demo delay
            # -------------------------------------------------

            await asyncio.sleep(0.1)

    except WebSocketDisconnect:
        print("WebSocket client disconnected")