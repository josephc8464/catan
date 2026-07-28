class Graph:
    """
    Undirected graph representing the Catan board topology.
    Vertices are integer IDs. Edges track adjacency and road color ownership.
    Neighbors stored as sets for O(1) lookup.
    """

    def __init__(self, size: int):
        self.adj_list: dict[int, set[int]] = {i: set() for i in range(size)}
        self.edge_color: dict[tuple[int, int], str | None] = {}

    def _canonical(self, u: int, v: int) -> tuple[int, int]:
        """
        Returns a single canonical key for an undirected edge.
        Eliminates the need to store and update both (u,v) and (v,u).
        """
        return (u, v) if u < v else (v, u)

    def has_edge(self, u: int, v: int) -> bool:
        """Returns True if an edge exists between u and v."""
        return v in self.adj_list[u]

    def add_edge(self, u: int, v: int) -> None:
        """Adds a bidirectional edge between u and v if it does not already exist."""
        if not self.has_edge(u, v):
            self.adj_list[u].add(v)
            self.adj_list[v].add(u)
            self.edge_color[self._canonical(u, v)] = None

    def remove_edge(self, u: int, v: int) -> None:
        """Removes the edge between u and v and its color entry."""
        if self.has_edge(u, v):
            self.adj_list[u].discard(v)
            self.adj_list[v].discard(u)
            self.edge_color.pop(self._canonical(u, v), None)

    def get_neighbors(self, node: int) -> set[int]:
        """Returns all neighboring vertex IDs for a given node."""
        return self.adj_list[node]

    def set_edge_color(self, u: int, v: int, color: str) -> bool:
        """
        Claims an edge with a player color. Only succeeds if the edge exists
        and is currently unoccupied (color is None).
        Returns True on success, False if already occupied or edge not found.
        """
        key = self._canonical(u, v)
        if key in self.edge_color and self.edge_color[key] is None:
            self.edge_color[key] = color
            return True
        return False

    def clear_edge_color(self, u: int, v: int) -> bool:
        """
        Resets an edge's color back to None.
        Used exclusively for rollback operations (e.g., failed Road Building card).
        Returns True on success, False if edge not found.
        """
        key = self._canonical(u, v)
        if key in self.edge_color:
            self.edge_color[key] = None
            return True
        return False

    def get_edge_color(self, u: int, v: int) -> str | None:
        """Returns the color of the road on edge (u, v), or None if unoccupied."""
        return self.edge_color.get(self._canonical(u, v))