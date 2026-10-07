import networkx as nx


def get_local_network(
    graph: nx.DiGraph,
    tx_id: str,
    hops: int = 1,
) -> nx.DiGraph:
    """Return a local subgraph around a transaction."""

    if tx_id not in graph:
        raise ValueError(f"Transaction not found in graph: {tx_id}")

    if hops < 1:
        raise ValueError("hops must be at least 1")

    nodes = nx.single_source_shortest_path_length(
        graph.to_undirected(),
        tx_id,
        cutoff=hops,
    ).keys()

    return graph.subgraph(nodes).copy()