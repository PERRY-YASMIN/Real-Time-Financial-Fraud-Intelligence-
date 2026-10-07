import networkx as nx


def get_neighbors(graph: nx.DiGraph, tx_id: str) -> dict[str, list[str]]:
    """Return the incoming and outgoing neighbors of a transaction."""

    incoming = list(graph.predecessors(tx_id))
    outgoing = list(graph.successors(tx_id))

    return {
        "incoming": incoming,
        "outgoing": outgoing,
    }