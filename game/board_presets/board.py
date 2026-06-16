from random import shuffle

from game.board_components import Graph, Vertex, Tile
from abc import ABC, abstractmethod

class Board(ABC):
    def __init__(self, num_vertices) -> None:
        self.graph = Graph(num_vertices)
        self.vertices = {i: Vertex(i) for i in range(num_vertices)}
        self.tiles = {}
        self.bank = {'wood': 19, 'brick': 19, 'sheep': 19, 'wheat': 19, 'ore': 19}
        self.development_cards = []
        self.tile_vertices = {i: [] for i in range(19)} 
        self.buildings = {i: None for i in range(54)} #None or tuple (building type, owner's color)
        self.robber_placement = 0
    
    def add_building(self, vertex, color, buildingType):
        self.buildings[vertex] = (buildingType, color)
        
    def add_tiles_vertices(self, vertexDict) -> None:
        for tile_id, vertices in vertexDict.items():
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
    
    @abstractmethod
    def setup_board(self) -> None:
        pass