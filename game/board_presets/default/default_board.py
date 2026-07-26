from random import shuffle

from game.board_components.default import Graph, Tile
from game.board_presets.default.board_context import BoardContext


class DefaultBoard:
    """Manages the state, topology, tiles, and pieces of the standard Catan board layout.
    
    Acts as the single source of truth for map connectivity, tile assignments,
    resource banks, port allocations, and placed buildings or roads.
    """

    def __init__(self) -> None:
        """Initializes an empty board state, initializing geometry, banks, and tracking fields."""
        self.board_context = BoardContext()

        # --- MAP & GEOMETRY ---
        self.graph = Graph(54)
        self.tiles: dict[int, Tile] = {}
        self.tile_vertices: dict[int, list[int]] = {i: [] for i in range(19)}

        # --- PIECES & BOARD STATE ---
        # Map of vertex ID to tuple of (structure_type, player_color)
        self.structures: dict[int, tuple[str | None, str | None]] = {
            i: (None, None) for i in range(54)
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
        self.development_cards: list[str] = []

        # --- ACHIEVEMENT TRACKING ---
        self.largest_army: str | None = None
        self.longest_road: str | None = None

    # =========================================================================
    # --- BOARD SETUP & INITIALIZATION ---
    # =========================================================================

    def setup_board(self) -> None:
        """Executes full board generation, including graph connectivity, tile shuffling,
        development deck creation, and port placements.
        """
        self._add_tiles()
        self._add_development_cards()
        self._setup_graph_connectivity()
        self._add_ports()

    def _add_tiles(self) -> None:
        """Generates the 19 standard tiles, shuffles resources, assigns dice values,
        and sets initial Robber position on the desert tile.
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

        for i in range(19):
            self.tiles[i] = Tile(tile_resources[i], 0, i)

        value_idx = 0
        for i in range(19):
            if self.tiles[i].resource != 'desert':
                self.tiles[i].number = tile_values[value_idx]
                value_idx += 1
            else:
                self.tiles[i].number = None
                self.robber_placement = self.tiles[i].tile_id

    def _add_development_cards(self) -> None:
        """Constructs and shuffles the standard 25-card development deck."""
        self.development_cards = (
            ['knight'] * 14
            + ['victory_point'] * 5
            + ['road_building'] * 2
            + ['year_of_plenty'] * 2
            + ['monopoly'] * 2
        )
        shuffle(self.development_cards)

    def _add_ports(self) -> None:
        """Randomly assigns port types (4 generic, 5 specific resources) across fixed port pairs."""
        port_types = self.board_context.RESOURCES + ['any'] * 4
        shuffle(port_types)

        for i, pair in enumerate(self.ports.keys()):
            self.ports[pair] = port_types[i]

    def _setup_graph_connectivity(self) -> None:
        """Builds the topology of the board by populating graph edges and tile-to-vertex mappings."""
        edges = [
            (0, 1), (0, 3), (1, 4), (2, 3), (2, 7), (3, 8),
            (4, 5), (4, 9), (5, 10), (6, 7), (6, 12), (7, 13),
            (8, 9), (8, 14), (9, 15), (10, 11), (10, 16), (11, 17),
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

        vertex_dict = {
            0:  [6, 7, 12, 13, 18, 19],
            1:  [18, 19, 24, 25, 30, 31],
            2:  [30, 31, 36, 37, 42, 43],
            3:  [2, 3, 7, 8, 13, 14],
            4:  [13, 14, 19, 20, 25, 26],
            5:  [25, 26, 31, 32, 37, 38],
            6:  [37, 38, 43, 44, 48, 49],
            7:  [0, 1, 3, 4, 8, 9],
            8:  [8, 9, 14, 15, 20, 21],
            9:  [20, 21, 26, 27, 32, 33],
            10: [32, 33, 38, 39, 44, 45],
            11: [44, 45, 49, 50, 52, 53],
            12: [4, 5, 9, 10, 15, 16],
            13: [15, 16, 21, 22, 27, 28],
            14: [27, 28, 33, 34, 39, 40],
            15: [39, 40, 45, 46, 50, 51],
            16: [10, 11, 16, 17, 22, 23],
            17: [22, 23, 28, 29, 34, 35],
            18: [34, 35, 40, 41, 46, 47]
        }
        for tile_id, vertices in vertex_dict.items():
            for vertex in vertices:
                self.tile_vertices[tile_id].append(vertex)

    # =========================================================================
    # --- GAME ACTIONS & MUTATORS ---
    # =========================================================================
    def add_bank_resource(self, resource: str, amount: int) -> None:
        """
        Adds a specified amount of a resource to the bank.
        """
        self.bank[resource] = self.bank.get(resource, 0) + amount

    def remove_bank_resource(self, resource: str, amount: int) -> bool:
        """
        Removes a specified amount of a resource from the bank if available.
        """
        if not self.bank_has_resource(resource, amount):
            return False
            
        self.bank[resource] -= amount
        return True

    def bank_has_resource(self, resource: str, amount: int) -> bool:
        """
        Checks if the bank contains at least the specified amount of a given resource.
        """
        return self.bank.get(resource, 0) >= amount
    
    def add_structure(self, vertex: int, color: str, structure_type: str) -> None:
        """Places or upgrades a building at a designated vertex location.
        
        Args:
            vertex: The vertex ID where the structure will be placed.
            color: The player color owning the building.
            structure_type: Type of structure (e.g., 'settlement', 'city').
        """
        self.structures[vertex] = (structure_type, color)
    
    
    def remove_structure(self, vertex: int) -> None:
        """Removes a building at a designated vertex location.
        
        Args:
            vertex: The vertex ID of which structure will be removed (None, None)
        """
        self.structures[vertex] = (None, None)
    
    def add_road(self, vertex1: int, vertex2: int, color: str) -> None:
        """Claims an edge between two vertices and assigns a player color road to it.
        
        Args:
            vertex1: Starting vertex ID of the edge.
            vertex2: Ending vertex ID of the edge.
            color: Player color claiming the road.
        """
        self.graph.set_edge_color(vertex1, vertex2, color)

    def remove_road(self, vertex1: int, vertex2: int) -> None:
        """Removes an edge between two vertices.
        
        Args:
            vertex1: Starting vertex ID of the edge.
            vertex2: Ending vertex ID of the edge.
        """
        self.graph.remove_edge(vertex1, vertex2)
    
    def get_top_dev_card(self) -> str | None:
        """Draws and returns the top card from the development deck.
        
        Returns:
            The card type as a string, or None if the deck is empty.
        """
        if not self.development_cards:
            return None
        return self.development_cards.pop(0)

    # =========================================================================
    # --- QUERIES & SPATIAL INSPECTION ---
    # =========================================================================
    def get_road_color(self, vertex1: int, vertex2: int) -> str | None:
        """Gets the color of the road present on an edge, if any.
        
        Args:
            vertex1: First vertex ID.
            vertex2: Second vertex ID.
            
        Returns:
            The color string of the road, or None if unoccupied.
        """
        return self.graph.get_edge_color(vertex1, vertex2)

    def get_port(self, vertices: tuple[int, int]) -> str | None:
        """
        Retrieves the port located at the specified edge vertices.
        """
        v1, v2 = vertices
        
        if (v1, v2) in self.ports:
            return self.ports[(v1, v2)]
        if (v2, v1) in self.ports:
            return self.ports[(v2, v1)]
            
        return None
    
    def get_port_for_tile(self, tile_id: int) -> tuple[tuple[int, int], str] | None:
        """Finds the port attached to a specific tile, if one exists.
        
        Args:
            tile_id: ID of the tile to query.
            
        Returns:
            A tuple of ((v1, v2), port_type) if a port touches this tile, else None.
        """
        tile_verts = self.tile_vertices[tile_id]
        for pair, resource in self.ports.items():
            v1, v2 = pair
            if v1 in tile_verts and v2 in tile_verts:
                return (pair, resource)
        return None

    def get_tile_vertices(self, tile_id: int) -> list[int] | None:
        """Retrieves the list of vertex IDs that form the perimeter of a given tile.

        Args:
            tile_id: The ID of the tile to query.

        Returns:
            A list of 6 vertex IDs belonging to the tile, or None if the tile_id is invalid.
        """
        return self.tile_vertices.get(tile_id, None)

    def get_structure(self, vertex: int) -> tuple[str | None, str | None]:
        """ Returns a structure at a given vertex, or (None, None) if it doesn't exist.

            Args:
                vertex: Vertex ID of the structure
        """
        return self.structures.get(vertex, (None, None))
    
    def has_road_neighbor(self, color: str, vertex: int) -> bool:
        """Checks if a single vertex touches at least one road owned by the target color.
        
        Useful for verifying settlement placement rules (ensuring a player builds 
        along their own road network).
        """
        for neighbor in self.graph.adj_list[vertex]:
            if self.graph.get_edge_color(neighbor, vertex) == color:
                return True
        return False

    def has_connected_neighbor(self, color: str, u: int, v: int) -> bool:
        """Checks if an edge (u, v) connects to any existing structure or road 
        owned by the target color at either endpoint.
        
        Useful for verifying road placement rules.
        """
        if self.structures[u][1] == color or self.structures[v][1] == color:
            return True

        return self.has_road_neighbor(color, u) or self.has_road_neighbor(color, v)

    def has_edge(self, vertex1: int, vertex2: int) -> bool:
        """Determines whether an edge exists between vertex1 and vertex2 in the board graph
        
        Returns:
            True if an edge exists between vertex1 and vertex2, false if not.
        """
        return self.graph.has_edge(vertex1, vertex2)
    
    def has_structure_neighbor(self, vertex: int) -> bool:
        """ Determines whether there is a structure adjacent near the target vertex regardless
        of color.

        Returns:
            True if a structure exists on a neighboring vertex (regardless of color), returns false if not.
        """
        for vertex in self.graph.get_neighbors(vertex):
            if self.get_structure(vertex) != (None, None):
                return True
            
        return False