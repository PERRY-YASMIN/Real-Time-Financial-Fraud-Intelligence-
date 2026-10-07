import networkx as nx
from community import community_louvain


def detect_communities(graph: nx.DiGraph) -> dict[str, int]:
    """Detect transaction communities using the Louvain algorithm."""

    undirected_graph = graph.to_undirected()

    partition = community_louvain.best_partition(
        undirected_graph,
        random_state=42,
    )

    return {
        str(tx_id): int(community_id)
        for tx_id, community_id in partition.items()
    }