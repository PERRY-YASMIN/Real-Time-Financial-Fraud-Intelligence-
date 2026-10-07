import asyncio

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from backend.engine.alerts import alert_manager
from backend.streaming.data_loader import load_transactions
from backend.api.routes import graph_manager, communities, processor
 
 
router = APIRouter()


# =========================================================
# WEBSOCKET STREAM
# =========================================================

@router.websocket("/ws/stream")
async def stream_transactions(websocket: WebSocket):
    """Stream transactions with real-time risk analysis."""

    await websocket.accept()

    transactions = load_transactions()

    active_timestep = None
    timestep_count = 0

    try:
        for transaction in transactions:
            # -------------------------------------------------
            # Track Option B completed timesteps
            # -------------------------------------------------
            if active_timestep is None:
                active_timestep = transaction.time_step
                timestep_count = 1
            elif transaction.time_step == active_timestep:
                timestep_count += 1
            else:
                # Timestep completed! Finalize Option B temporal context
                from backend.ml.temporal import get_temporal_detector
                det = get_temporal_detector()
                det.record_timestep(active_timestep, count=timestep_count)

                timestep_event = {
                    "type": "timestep_completed",
                    "time_step": active_timestep,
                    "transaction_count": timestep_count,
                    "temporal_context": det.score_transaction({
                        "txId": transaction.tx_id,
                        "time_step": active_timestep,
                    }),
                }
                await websocket.send_json(timestep_event)

                active_timestep = transaction.time_step
                timestep_count = 1

            # -------------------------------------------------
            # Analyze transaction via integrated Person 1 ML & temporal
            # -------------------------------------------------
            result = processor.process(
                transaction=transaction,
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
            # Send transaction event with unified contract
            # -------------------------------------------------
            event = {
                "type": "transaction",
                "transaction": {
                    "id": transaction.tx_id,
                    "txId": transaction.tx_id,
                    "time_step": transaction.time_step,
                    "ml_score": result["ml_score"],
                    "predicted_class": result["predicted_class"],
                    "threshold": result["threshold"],
                    "temporal_score": result["temporal_score"],
                    "temporal_reasons": result["temporal_reasons"],
                    "risk_factors": result["risk_factors"],
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
                await websocket.send_json(alert_event)

            # -------------------------------------------------
            # Demo delay
            # -------------------------------------------------
            await asyncio.sleep(0.1)


    except WebSocketDisconnect:
        print("WebSocket client disconnected")