from backend.engine.analyzer import analyze_transaction


class StreamProcessor:
    """Process incoming transactions through the risk engine."""

    def __init__(self, graph_manager, communities):
        self.graph_manager = graph_manager
        self.communities = communities

    def process(
        self,
        transaction,
        ml_score: float,
        temporal_score: float,
    ) -> dict:
        """Analyze one incoming transaction."""

        tx_id = transaction.tx_id

        graph_score = self._calculate_graph_score(tx_id)

        analysis = analyze_transaction(
            ml_score=ml_score,
            graph_score=graph_score,
            temporal_score=temporal_score,
        )

        return {
            "transaction_id": tx_id,
            "time_step": transaction.time_step,
            "analysis": analysis,
        }

    def _calculate_graph_score(self, tx_id: str) -> float:
        """Calculate graph risk for a transaction."""

        from backend.engine.graph_analyzer import analyze_graph_transaction

        return analyze_graph_transaction(
            graph_manager=self.graph_manager,
            communities=self.communities,
            tx_id=tx_id,
        )