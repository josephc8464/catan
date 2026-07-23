from game.board_presets.default.default_board import DefaultBoard
from game.board_components.default import Tile

class TestBoard(DefaultBoard):
    """
    A deterministic version of DefaultBoard for headless testing.
    Overrides randomization methods to remove shuffle() calls.
    """
    
    def add_tiles(self) -> None:
        # Hardcoded from Board, but without shuffle(tile_resources)
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
        # Standard card list, without shuffle(self.development_cards)
        self.development_cards = (
            ['knight'] * 14 + 
            ['victory_point'] * 5 + 
            ['road_building'] * 2 + 
            ['year_of_plenty'] * 2 + 
            ['monopoly'] * 2
        )

    def add_ports(self) -> None:
        # Standard port list, without shuffle
        port_types = self.board_context.RESOURCES + ['any'] * 4
    
        for i, pair in enumerate(self.ports.keys()):
            self.ports[pair] = port_types[i]