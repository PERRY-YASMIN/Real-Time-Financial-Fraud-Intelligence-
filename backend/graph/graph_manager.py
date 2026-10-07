import networkx as nx

from backend.graph.edge_loader import load_edges
from backend.streaming.data_loader import load_transactions


class GraphManager:
    """Manages the transaction graph."""

    def __init__(self):
        self.graph = nx.DiGraph()

        # Cached graph statistics
        self.min_degree = 0
        self.max_degree = 0

        # Cached community statistics
        self.community_sizes = {}
        self.community_densities = {}

    def load_graph(self):
        """Load transactions and relationships into the graph."""

        transactions = load_transactions()
        edges = load_edges()

        for transaction in transactions:
            self.add_transaction(
                tx_id=transaction.tx_id,
                time_step=transaction.time_step,
            )

        for source_id, target_id in edges:
            self.add_transaction_edge(
                source_id=source_id,
                target_id=target_id,
            )

        self._calculate_graph_statistics()

    def add_transaction(
        self,
        tx_id: str,
        time_step: int,
    ):
        """Add a transaction as a node."""

        self.graph.add_node(
            tx_id,
            time_step=time_step,
        )

    def add_transaction_edge(
        self,
        source_id: str,
        target_id: str,
    ):
        """Add a directed relationship between two transactions."""

        self.graph.add_edge(
            source_id,
            target_id,
        )

    def _calculate_graph_statistics(self):
        """Calculate statistics that can be reused during analysis."""

        degrees = [
            degree
            for _, degree in self.graph.degree()
        ]

        if degrees:
            self.min_degree = min(degrees)
            self.max_degree = max(degrees)

    def set_community_statistics(
        self,
        communities: dict[str, int],
    ):
        """Calculate and cache community sizes and densities."""

        community_nodes = {}

        for tx_id, community_id in communities.items():
            community_nodes.setdefault(
                community_id,
                [],
            ).append(tx_id)

        for community_id, nodes in community_nodes.items():
            self.community_sizes[community_id] = len(nodes)

            subgraph = (
                self.graph
                .subgraph(nodes)
                .to_undirected()
            )

            self.community_densities[community_id] = nx.density(
                subgraph
            )

    def node_count(self) -> int:
        """Return the number of transaction nodes."""

        return self.graph.number_of_nodes()

    def edge_count(self) -> int:
        """Return the number of transaction edges."""

        return self.graph.number_of_edges()