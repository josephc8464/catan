from random import shuffle

from game.board_components.default import Graph, Tile
from game.board_presets.default.board_context import BoardContext

class DefaultBoard():
    def __init__(self) -> None:
        self.board_context = BoardContext()

        # --- MAP & GEOMETRY ---
        self.graph = Graph(54)
        self.tiles: dict[int, Tile] = {}
        self.tile_vertices: dict[int, list[int]] = {i: [] for i in range(19)} 

        # --- PIECES & BOARD STATE ---
        self.buildings: dict[int, tuple[str | None, str | None]] = {i: (None, None) for i in range(54)}
        self.ports: dict[tuple[int, int], str] = {pair: "" for pair in [(36, 42), (18, 24), (48, 49), (2, 7), (0, 1), (50, 51), (5, 10), (41, 47), (23, 29)]}
        self.robber_placement: int = 0
        
        # --- GAME ECONOMY ---
        self.bank: dict[str, int] = {resource: 19 for resource in self.board_context.RESOURCES}
        self.development_cards: list[str] = []

        #Tracked by player colors
        self.largest_army: str | None = None
        self.longest_road: str | None = None

    def get_top_dev_card(self) -> str:
        card = self.development_cards.pop(0)
        return card
    
    def has_color_neighbor(self, color, u, v) -> bool:
        if self.buildings[u] is not None and self.buildings[u][1] == color:
            return True
        if self.buildings[v] is not None and self.buildings[v][1] == color:
            return True
        
        for vertex_edge in self.graph.adj_list[u]:
            if self.graph.get_edge_color(vertex_edge, u) == color:
                return True
        
        for vertex_edge in self.graph.adj_list[v]:
            if self.graph.get_edge_color(vertex_edge, v) == color:
                return True
        
        return False
    
    def get_port_for_tile(self, tile_id):
        tile_verts = self.tile_vertices[tile_id]
        for pair, resource in self.ports.items():
            v1, v2 = pair
            if v1 in tile_verts and v2 in tile_verts:
                return (pair, resource)
        return None

    def add_road(self, vertex1, vertex2, color) -> None:
        self.graph.set_edge_color(vertex1, vertex2, color)
    
    def get_road_color(self, vertex1, vertex2) -> str | None:
        return self.graph.get_edge_color(vertex1, vertex2)

    def add_building(self, vertex, color, building_type) -> None:
        self.buildings[vertex] = (building_type, color)
    
    def add_ports(self) -> None:
        port_types = self.board_context.RESOURCES + ['any'] * 4
        shuffle(port_types)
    
        for i, pair in enumerate(self.ports.keys()):
            self.ports[pair] = port_types[i]
                                 
    def add_tiles_vertices(self, vertex_dict) -> None:
        for tile_id, vertices in vertex_dict.items():
            for vertex in vertices:
                self.tile_vertices[tile_id].append(vertex)

    def add_tiles(self) -> None:
        #Does the normal mode variation for non-beginners
        tile_values = [
            5, 2,  6,  3, 8, 10,
            9, 12, 11, 4, 8, 10,
            9, 4,  5,  6, 3, 11
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
        
        j = 0
        for i in range(19):
            if self.tiles[i].resource != 'desert':
                self.tiles[i].number = tile_values[j]
                j += 1
            else:
                self.tiles[i].number = None
                self.robber_placement = self.tiles[i].tile_id

    def add_development_cards(self) -> None:
        self.development_cards = ['knight'] * 14 + ['victory_point'] * 5 + ['road_building'] * 2 + ['year_of_plenty'] * 2 + ['monopoly'] * 2
        shuffle(self.development_cards)

    def add_connectivity(self, edges) -> None:
        #Manually add edges based on the board layout
        for u, v in edges:
            self.graph.add_edge(u, v)

    def setup_board(self) -> None:
        self.add_tiles()
        self.add_development_cards()
        
        edges = [
            (0, 1), (0, 3), (1, 4),
            (2, 3), (2, 7), (3, 8),
            (4, 5), (4, 9), (5, 10),
            (6, 7), (6, 12), (7, 13),
            (8, 9), (8, 14), (9, 15),
            (10, 11), (10, 16), (11, 17),
            (12, 18), (13, 14), (13, 19),
            (14, 20), (15, 16), (15, 21),
            (16, 22), (17, 23), (18, 19),
            (18, 24), (19, 25), (20, 21),
            (20, 26), (21, 27), (22, 23),
            (22, 28), (23, 29), (24, 30),
            (25, 26), (25, 31), (26, 32),
            (27, 28), (27, 33), (28, 34),
            (29, 35), (30, 31), (30, 36),
            (31, 37), (32, 33), (32, 38),
            (33, 39), (34, 35), (34, 40),
            (35, 41), (36, 42), (37, 38),
            (37, 43), (38, 44), (39, 40),
            (39, 45), (40, 46), (41, 47),
            (42, 43), (43, 48), (44, 45),
            (44, 49), (45, 50), (46, 47),
            (46, 51), (48, 49), (49, 52),
            (50, 51), (50, 53), (52, 53),
        ]
        self.add_connectivity(edges)

        vertex_dict = {
            0:  [6,7,12,13,18,19],
            1:  [18,19,24,25,30,31],
            2:  [30,31,36,37,42,43],
            3:  [2,3,7,8,13,14],
            4:  [13,14,19,20,25,26],
            5:  [25,26,31,32,37,38],
            6:  [37,38,43,44,48,49],
            7:  [0,1,3,4,8,9],
            8:  [8,9,14,15,20,21],
            9:  [20,21,26,27,32,33],
            10: [32,33,38,39,44,45],
            11: [44,45,49,50,52,53],
            12: [4,5,9,10,15,16],
            13: [15,16,21,22,27,28],
            14: [27,28,33,34,39,40],
            15: [39,40,45,46,50,51],
            16: [10,11,16,17,22,23],
            17: [22,23,28,29,34,35],
            18: [34,35,40,41,46,47]
        }   
        self.add_tiles_vertices(vertex_dict)

        self.add_ports()


    

        

    
    