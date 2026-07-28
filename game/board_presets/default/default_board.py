from collections import deque
from random import shuffle

from game.board_components.default import Graph, Tile
from game.board_presets.default.board_context import BoardContext


class DefaultBoard:
    """
    Manages the state, topology, tiles, and pieces of the standard Catan board layout.
    Acts as the single source of truth for map connectivity, tile assignments,
    resource banks, port allocations, and placed buildings or roads.

    ValueError contract:
        Raised when caller passes input not defined in BoardContext
        (unknown structure type, resource, or out-of-bounds vertex).
        This is a programming error, not a recoverable game condition.
    """

    VERTEX_COUNT: int = 54
    TILE_COUNT: int = 19

    def __init__(self) -> None:
        """Initializes an empty board state, including geometry, banks, and tracking fields."""
        self.board_context = BoardContext()

        # --- MAP & GEOMETRY ---
        self.graph = Graph(self.VERTEX_COUNT)
        self.tiles: dict[int, Tile] = {}

        self.tile_vertices: dict[int, list[int]] = {
            0:  [6,  7,  12, 13, 18, 19],
            1:  [18, 19, 24, 25, 30, 31],
            2:  [30, 31, 36, 37, 42, 43],
            3:  [2,  3,  7,  8,  13, 14],
            4:  [13, 14, 19, 20, 25, 26],
            5:  [25, 26, 31, 32, 37, 38],
            6:  [37, 38, 43, 44, 48, 49],
            7:  [0,  1,  3,  4,  8,  9 ],
            8:  [8,  9,  14, 15, 20, 21],
            9:  [20, 21, 26, 27, 32, 33],
            10: [32, 33, 38, 39, 44, 45],
            11: [44, 45, 49, 50, 52, 53],
            12: [4,  5,  9,  10, 15, 16],
            13: [15, 16, 21, 22, 27, 28],
            14: [27, 28, 33, 34, 39, 40],
            15: [39, 40, 45, 46, 50, 51],
            16: [10, 11, 16, 17, 22, 23],
            17: [22, 23, 28, 29, 34, 35],
            18: [34, 35, 40, 41, 46, 47],
        }

        # --- PIECES & BOARD STATE ---
        #(structure type, color owner)
        self.structures: dict[int, tuple[str | None, str | None]]  = {
            i: (None, None) for i in range(self.VERTEX_COUNT)
        }

        self.ports: dict[tuple[int, int], str] = {
            pair: "" for pair in [
                (36, 42), (18, 24), (48, 49), (2, 7), (0, 1),
                (50, 51), (5, 10), (41, 47), (23, 29)
            ]
        }
        self.robber_placement: int = 0

        # --- GAME ECONOMY ---
        self.bank: dict[str, int] = {
            resource: 19 for resource in self.board_context.RESOURCES
        }
        self.development_cards: deque[str] = deque()

        # --- ACHIEVEMENT TRACKING ---
        self.largest_army: str | None = None
        self.longest_road: str | None = None

    # =========================================================================

    # --- VALIDATORS ---

    # =========================================================================

    def _validate_vertex(self, vertex: int) -> None:
        """
        Raises ValueError if the vertex ID is outside the valid board range.
        Called as a guard in all structure and query methods.
        BoardContext has no knowledge of board geometry — this guard lives here.
        """
        if vertex not in self.structures:
            raise ValueError(f"Vertex {vertex} is out of range for this board.")

    # =========================================================================

    # --- BOARD SETUP & INITIALIZATION ---

    # =========================================================================

    def setup_board(self) -> None:
        """
        Executes full board generation: graph connectivity, tile shuffling,
        development deck creation, and port placements.
        """
        self._setup_graph_connectivity()
        self._add_tiles()
        self._add_development_cards()
        self._add_ports()

    def _add_tiles(self) -> None:
        """
        Generates the 19 standard tiles, shuffles resources, assigns dice values,
        and sets the initial robber position on the desert tile.
        Each Tile is constructed fully in one pass — no post-construction mutation.
        """
        tile_values = [
            5, 2, 6, 3, 8, 10,
            9, 12, 11, 4, 8, 10,
            9, 4, 5, 6, 3, 11
        ]
        tile_resources = [
            'wood', 'sheep', 'wheat', 'brick', 'ore', 'desert',
            'wood', 'sheep', 'wheat', 'brick', 'ore',
            'wood', 'sheep', 'wheat', 'brick', 'ore',
            'wood', 'sheep', 'wheat'
        ]

        shuffle(tile_resources)

        value_idx = 0
        for i, resource in enumerate(tile_resources):
            if resource == 'desert':
                self.tiles[i] = Tile(tile_id=i, resource=resource, number=None)
                self.robber_placement = i
            else:
                self.tiles[i] = Tile(tile_id=i, resource=resource, number=tile_values[value_idx])
                value_idx += 1

    def _add_development_cards(self) -> None:
        """Constructs and shuffles the standard 25-card development deck."""
        cards = (
            ['knight'] * 14
            + ['victory_point'] * 5
            + ['road_building'] * 2
            + ['year_of_plenty'] * 2
            + ['monopoly'] * 2
        )
        shuffle(cards)
        self.development_cards = deque(cards)

    def _add_ports(self) -> None:
        """Randomly assigns port types (4 generic, 5 specific resources) across fixed port pairs."""
        port_types = list(self.board_context.RESOURCES) + ['any'] * 4
        shuffle(port_types)
        for pair, port_type in zip(self.ports.keys(), port_types):
            self.ports[pair] = port_type

    def _setup_graph_connectivity(self) -> None:
        """Builds the board topology by populating graph edges."""
        edges = [
            (0, 1),   (0, 3),   (1, 4),   (2, 3),   (2, 7),   (3, 8),
            (4, 5),   (4, 9),   (5, 10),  (6, 7),   (6, 12),  (7, 13),
            (8, 9),   (8, 14),  (9, 15),  (10, 11), (10, 16), (11, 17),
            (12, 18), (13, 14), (13, 19), (14, 20), (15, 16), (15, 21),
            (16, 22), (17, 23), (18, 19), (18, 24), (19, 25), (20, 21),
            (20, 26), (21, 27), (22, 23), (22, 28), (23, 29), (24, 30),
            (25, 26), (25, 31), (26, 32), (27, 28), (27, 33), (28, 34),
            (29, 35), (30, 31), (30, 36), (31, 37), (32, 33), (32, 38),
            (33, 39), (34, 35), (34, 40), (35, 41), (36, 42), (37, 38),
            (37, 43), (38, 44), (39, 40), (39, 45), (40, 46), (41, 47),
            (42, 43), (43, 48), (44, 45), (44, 49), (45, 50), (46, 47),
            (46, 51), (48, 49), (49, 52), (50, 51), (50, 53), (52, 53),
        ]
        for u, v in edges:
            self.graph.add_edge(u, v)

    # =========================================================================

    # --- GAME ACTIONS & MUTATORS ---

    # =========================================================================

    def add_bank_resource(self, resource: str, amount: int) -> None:
        """
        Adds a specified amount of a resource to the bank.
        Raises ValueError if the resource is not defined in BoardContext.
        """
        self.board_context.validate_resource(resource)
        self.bank[resource] = self.bank.get(resource, 0) + amount

    def remove_bank_resource(self, resource: str, amount: int) -> bool:
        """
        Removes a specified amount of a resource from the bank if available.
        Raises ValueError if the resource is not defined in BoardContext.
        Returns False if the bank has insufficient stock — valid game state.
        """
        self.board_context.validate_resource(resource)
        if not self.bank_has_resource(resource, amount):
            return False
        self.bank[resource] -= amount
        return True

    def bank_has_resource(self, resource: str, amount: int) -> bool:
        """
        Returns True if the bank holds at least the specified amount.
        Raises ValueError if the resource is not defined in BoardContext.
        """
        self.board_context.validate_resource(resource)
        return self.bank.get(resource, 0) >= amount

    def add_structure(self, vertex: int, color: str, structure_type: str) -> None:
        """
        Places or upgrades a building at a designated vertex.
        Raises ValueError if vertex is out of range or structure type is unknown.
        """
        self._validate_vertex(vertex)
        self.board_context.validate_structure(structure_type)
        self.structures[vertex] = (structure_type, color)

    def remove_structure(self, vertex: int) -> None:
        """
        Clears the structure at a designated vertex.
        Raises ValueError if vertex is out of range.
        """
        self._validate_vertex(vertex)
        self.structures[vertex] = (None, None)

    def add_road(self, vertex1: int, vertex2: int, color: str) -> None:
        """
        Claims an edge between two vertices and assigns a player color road to it.
        Raises ValueError if either vertex is out of range.
        """
        self._validate_vertex(vertex1)
        self._validate_vertex(vertex2)
        self.graph.set_edge_color(vertex1, vertex2, color)

    def remove_road(self, vertex1: int, vertex2: int) -> None:
        """
        Removes the road on an edge between two vertices.
        Raises ValueError if either vertex is out of range.
        """
        self._validate_vertex(vertex1)
        self._validate_vertex(vertex2)
        self.graph.remove_edge(vertex1, vertex2)

    def get_top_dev_card(self) -> str | None:
        """
        Draws and returns the top card from the development deck.
        Returns None if the deck is empty.
        Uses deque.popleft() for O(1) removal from the front.
        """
        return self.development_cards.popleft() if self.development_cards else None

    # =========================================================================

    # --- QUERIES & SPATIAL INSPECTION ---

    # =========================================================================

    def get_road_color(self, vertex1: int, vertex2: int) -> str | None:
        """Returns the color of the road on an edge, or None if unoccupied."""
        return self.graph.get_edge_color(vertex1, vertex2)

    @staticmethod
    def _canonical_port(v1: int, v2: int) -> tuple[int, int]:
        """
        Returns a canonical key for a port edge.
        Mirrors Graph._canonical — eliminates dual-direction lookup.
        """
        return (v1, v2) if v1 < v2 else (v2, v1)

    def get_port(self, vertices: tuple[int, int]) -> str | None:
        """Returns the port type at the specified edge vertices, or None if no port exists."""
        return self.ports.get(self._canonical_port(*vertices))

    def get_port_for_tile(self, tile_id: int) -> tuple[tuple[int, int], str] | None:
        """
        Finds the port attached to a specific tile, if one exists.
        Returns ((v1, v2), port_type) or None.
        """
        tile_verts = self.tile_vertices[tile_id]
        return next(
            ((pair, resource) for pair, resource in self.ports.items()
             if pair[0] in tile_verts and pair[1] in tile_verts),
            None
        )

    def get_tile_vertices(self, tile_id: int) -> list[int] | None:
        """Returns the list of vertex IDs that form the perimeter of a tile, or None if invalid."""
        return self.tile_vertices.get(tile_id)

    def get_structure(self, vertex: int) -> tuple[str | None, str | None]:
        """
        Returns the (structure_type, color) at a vertex, or (None, None) if empty.
        Raises ValueError if vertex is out of range.
        """
        self._validate_vertex(vertex)
        return self.structures.get(vertex, (None, None))

    def has_road_neighbor(self, color: str, vertex: int) -> bool:
        """
        Returns True if the vertex touches at least one road owned by the given color.
        Used to verify settlement placement connectivity.
        """
        return any(
            self.graph.get_edge_color(neighbor, vertex) == color
            for neighbor in self.graph.adj_list[vertex]
        )

    def has_connected_neighbor(self, color: str, u: int, v: int) -> bool:
        """
        Returns True if edge (u, v) connects to any existing structure or road
        owned by the given color at either endpoint.
        Used to verify road placement connectivity.
        """
        if self.structures[u][1] == color or self.structures[v][1] == color:
            return True
        return self.has_road_neighbor(color, u) or self.has_road_neighbor(color, v)

    def has_edge(self, vertex1: int, vertex2: int) -> bool:
        """Returns True if an edge exists between vertex1 and vertex2."""
        return self.graph.has_edge(vertex1, vertex2)

    def has_structure_neighbor(self, vertex: int) -> bool:
        """
        Returns True if any vertex adjacent to the given vertex holds a structure.
        Used to enforce the distance rule during settlement placement.
        """
        return any(
            self.get_structure(v) != (None, None)
            for v in self.graph.get_neighbors(vertex)
        )