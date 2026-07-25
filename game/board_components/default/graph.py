class Graph:
    """
    Undirected graph representing the Catan board topology.
    Vertices are integer IDs. Edges track adjacency and road color ownership.
    """

    def __init__(self, size: int):
        self.adj_list: dict[int, list[int]] = {i: [] for i in range(size)}
        self.edge_color: dict[tuple[int, int], str | None] = {}

    def has_edge(self, u: int, v: int) -> bool:
        """Returns True if an edge exists between u and v."""
        return v in self.adj_list[u]

    def add_edge(self, u: int, v: int) -> None:
        """Adds a bidirectional edge between u and v if it does not already exist."""
        if v not in self.adj_list[u] and u not in self.adj_list[v]:
            self.adj_list[u].append(v)
            self.adj_list[v].append(u)
            self.edge_color[(u, v)] = None
            self.edge_color[(v, u)] = None

    def remove_edge(self, u: int, v: int) -> None:
        """Removes the edge between u and v and its color entries."""
        if v in self.adj_list[u] and u in self.adj_list[v]:
            self.adj_list[u].remove(v)
            self.adj_list[v].remove(u)
            del self.edge_color[(u, v)]
            del self.edge_color[(v, u)]

    def get_neighbors(self, node: int) -> list[int]:
        """Returns all neighboring vertex IDs for a given node."""
        return self.adj_list[node]

    def set_edge_color(self, u: int, v: int, color: str) -> bool:
        """
        Claims an edge with a player color. Only succeeds if the edge exists
        and is currently unoccupied (color is None).
        Returns True on success, False if already occupied or edge not found.
        """
        if (u, v) in self.edge_color and self.edge_color[(u, v)] is None:
            self.edge_color[(u, v)] = color
            self.edge_color[(v, u)] = color
            return True
        return False

    def clear_edge_color(self, u: int, v: int) -> bool:
        """
        Resets an edge's color back to None.
        Used exclusively for rollback operations (e.g., failed Road Building card).
        Returns True on success, False if edge not found.
        """

        if (u, v) in self.edge_color:
            self.edge_color[(u, v)] = None
            self.edge_color[(v, u)] = None
            return True
        return False

    def get_edge_color(self, u: int, v: int) -> str | None:
        """Returns the color of the road on edge (u, v), or None if unoccupied."""
        return self.edge_color.get((u, v))