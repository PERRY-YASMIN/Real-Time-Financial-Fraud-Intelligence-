import json
from pathlib import Path
import networkx as nx
from community import community_louvain


CACHE_PATH = (
    Path(__file__).resolve().parents[2]
    / "data"
    / "processed"
    / "communities_cache.json"
)


def detect_communities(graph: nx.DiGraph, use_cache: bool = True) -> dict[str, int]:
    """Detect transaction communities using the Louvain algorithm."""

    # 1. Check for cached partition to ensure instant startup
    if use_cache and CACHE_PATH.exists():
        with open(CACHE_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
            # Only use cache if all nodes in graph are present in cache
            if all(str(n) in data for n in graph.nodes()):
                return {str(tx_id): int(cid) for tx_id, cid in data.items()}

    undirected_graph = graph.to_undirected()

    partition = community_louvain.best_partition(
        undirected_graph,
        random_state=42,
    )

    result = {
        str(tx_id): int(community_id)
        for tx_id, community_id in partition.items()
    }

    if use_cache:
        try:
            with open(CACHE_PATH, "w", encoding="utf-8") as f:
                json.dump(result, f)
        except Exception:
            pass

    return result