import networkx as nx


def get_community_size(
    graph: nx.DiGraph,
    communities: dict[str, int],
    tx_id: str,
) -> int:
    """Return the number of transactions in the same community."""

    if tx_id not in graph:
        raise ValueError(f"Transaction not found in graph: {tx_id}")

    if tx_id not in communities:
        raise ValueError(f"Community not found for transaction: {tx_id}")

    community_id = communities[tx_id]

    return sum(
        1
        for node in graph.nodes
        if communities.get(node) == community_id
    )


def get_community_density(
    graph: nx.DiGraph,
    communities: dict[str, int],
    tx_id: str,
) -> float:
    """Return the internal connectivity density of a transaction's community."""

    if tx_id not in graph:
        raise ValueError(f"Transaction not found in graph: {tx_id}")

    if tx_id not in communities:
        raise ValueError(f"Community not found for transaction: {tx_id}")

    community_id = communities[tx_id]

    community_nodes = [
        node
        for node in graph.nodes
        if communities.get(node) == community_id
    ]

    subgraph = graph.subgraph(community_nodes).to_undirected()

    return nx.density(subgraph)