import networkx as nx


def get_in_degree(graph: nx.DiGraph, tx_id: str) -> int:
    """Return the number of incoming connections for a transaction."""

    return graph.in_degree(tx_id)


def get_out_degree(graph: nx.DiGraph, tx_id: str) -> int:
    """Return the number of outgoing connections for a transaction."""

    return graph.out_degree(tx_id)


def get_total_degree(graph: nx.DiGraph, tx_id: str) -> int:
    """Return the total number of incoming and outgoing connections."""

    return graph.degree(tx_id)