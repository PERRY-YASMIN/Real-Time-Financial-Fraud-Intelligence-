import networkx as nx

from backend.graph.scoring import min_max_normalize


def calculate_graph_score(
    graph: nx.DiGraph,
    communities: dict[str, int],
    tx_id: str,
    min_degree: int,
    max_degree: int,
    community_sizes: dict[int, int],
    community_densities: dict[int, float],
) -> float:
    """Calculate an explainable graph risk score."""

    if tx_id not in graph:
        raise ValueError(f"Transaction not found in graph: {tx_id}")

    if tx_id not in communities:
        raise ValueError(f"Community not found for transaction: {tx_id}")

    # ---------------------------------------------------------
    # 1. Connectivity score
    # ---------------------------------------------------------

    degree = graph.degree(tx_id)

    connectivity_score = min_max_normalize(
        degree,
        min_degree,
        max_degree,
    )

    # ---------------------------------------------------------
    # 2. Community information
    # ---------------------------------------------------------

    community_id = communities[tx_id]

    community_size = community_sizes[community_id]
    community_density = community_densities[community_id]

    # ---------------------------------------------------------
    # 3. Normalize community size
    # ---------------------------------------------------------

    all_community_sizes = list(
        community_sizes.values()
    )

    size_min = min(all_community_sizes)
    size_max = max(all_community_sizes)

    community_size_score = min_max_normalize(
        community_size,
        size_min,
        size_max,
    )

    # ---------------------------------------------------------
    # 4. Combine graph signals
    # ---------------------------------------------------------

    graph_score = (
        0.50 * connectivity_score
        + 0.30 * community_density
        + 0.20 * community_size_score
    )

    return max(0.0, min(graph_score, 1.0))