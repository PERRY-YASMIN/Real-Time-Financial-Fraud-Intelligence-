from backend.graph.risk import calculate_graph_score


def analyze_graph_transaction(
    graph_manager,
    communities: dict[str, int],
    tx_id: str,
) -> float:
    """Calculate graph risk for a real transaction."""

    graph_score = calculate_graph_score(
        graph=graph_manager.graph,
        communities=communities,
        tx_id=tx_id,
        min_degree=graph_manager.min_degree,
        max_degree=graph_manager.max_degree,
        community_sizes=graph_manager.community_sizes,
        community_densities=graph_manager.community_densities,
    )

    return round(graph_score, 4)