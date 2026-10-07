from typing import Optional, Dict, Any, Union

from backend.engine.analyzer import analyze_transaction
from backend.streaming.data_loader import get_transaction_features
from backend.ml.inference import predict_transaction
from backend.ml.temporal import score_transaction


class StreamProcessor:
    """Process incoming transactions through the risk engine."""

    def __init__(self, graph_manager, communities):
        self.graph_manager = graph_manager
        self.communities = communities

    def process(
        self,
        transaction,
        ml_score: Optional[float] = None,
        temporal_score: Optional[float] = None,
    ) -> dict:
        """
        Analyze one incoming transaction.
        Integrates:
        - Person 1 frozen XGBoost ML inference (zero latency)
        - Person 1 Option B temporal intelligence (rolling velocity context)
        - Person 2 graph intelligence (Louvain community & connectivity topology)
        - Person 2 multi-signal risk aggregation
        """
        if hasattr(transaction, "tx_id"):
            tx_id = str(transaction.tx_id)
            time_step = int(transaction.time_step)
        elif isinstance(transaction, dict):
            tx_id = str(transaction.get("txId", transaction.get("tx_id", "")))
            time_step = int(transaction.get("time_step", 1))
        else:
            tx_id = str(getattr(transaction, "tx_id", ""))
            time_step = int(getattr(transaction, "time_step", 1))

        # ---------------------------------------------------------
        # 1. Person 1 ML Inference (Zero-Latency)
        # ---------------------------------------------------------
        if ml_score is not None:
            ml_val = float(ml_score)
            predicted_class = "ILLICIT" if ml_val >= 0.69 else "LICIT"
            threshold = 0.69
        else:
            features = get_transaction_features(tx_id)
            if features is not None:
                ml_res = predict_transaction(features)
                ml_val = float(ml_res["ml_score"])
                predicted_class = ml_res["predicted_class"]
                threshold = float(ml_res["threshold"])
            else:
                ml_val = 0.0
                predicted_class = "LICIT"
                threshold = 0.69

        # ---------------------------------------------------------
        # 2. Person 1 Temporal Intelligence (Option B)
        # ---------------------------------------------------------
        if temporal_score is not None:
            temp_val = float(temporal_score)
            temporal_reasons = []
        else:
            temp_res = score_transaction({
                "txId": tx_id,
                "time_step": time_step,
            })
            temp_val = float(temp_res["temporal_score"])
            temporal_reasons = temp_res.get("temporal_reasons", [])

        # ---------------------------------------------------------
        # 3. Person 2 Graph Intelligence
        # ---------------------------------------------------------
        graph_score = self._calculate_graph_score(tx_id)

        # ---------------------------------------------------------
        # 4. Person 2 Multi-Signal Risk Aggregation
        # ---------------------------------------------------------
        analysis = analyze_transaction(
            ml_score=ml_val,
            graph_score=graph_score,
            temporal_score=temp_val,
        )

        return {
            "transaction_id": tx_id,
            "txId": tx_id,
            "time_step": time_step,
            "ml_score": round(ml_val, 6),
            "predicted_class": predicted_class,
            "threshold": threshold,
            "temporal_score": round(temp_val, 6),
            "temporal_reasons": temporal_reasons,
            "risk_factors": [],
            "analysis": analysis,
        }

    def _calculate_graph_score(self, tx_id: str) -> float:
        """Calculate graph risk for a transaction."""
        from backend.engine.graph_analyzer import analyze_graph_transaction

        if self.graph_manager is None or self.communities is None:
            return 0.0

        if str(tx_id) not in self.graph_manager.graph or str(tx_id) not in self.communities:
            return 0.0

        try:
            return analyze_graph_transaction(
                graph_manager=self.graph_manager,
                communities=self.communities,
                tx_id=str(tx_id),
            )
        except Exception:
            return 0.0