import math

import pygame
from rendering.default.board.board_renderer_components.sprites import Hex, Structure, Road, Token
from rendering.utils import ColorUtility, PositionUtility
from game.board_presets.default.default_board import DefaultBoard

class DynamicSpriteManager():
    """
    Manager for dynamic sprites.
    
    Sprites that change throughout gameplay, such as: the robber, buildings (city and settlements), 
    and roads are managed here. DynamicSpriteManager creates the corresponding sprites, then scales
    and rotates to the correct position. DynamicSpriteManager loads new sprites on input.
    
    Attributes:
        board: The board being rendered.
        pos_util: Reference for positioning sprites on the screen.
        color_util: Reference for RGB colors, used in Roads and Buildings.
    """  

    def __init__(self, board: DefaultBoard):
        self._load_sprite_images()
        
        self.board = board
        self.pos_util = PositionUtility()
        self.color_util = ColorUtility()
    
    def _load_sprite_images(self):
        ''' Init for global image dictionaries '''
        Token.load_images()
        Road.load_images()
        Structure.load_images()

    def update_roads(self, vertex_positions: dict[int, tuple[float, float]], road_size: list[int]) -> list[Road]:
        ''' Creates new road sprites based on vertex positions. '''

        road_sprites = []

        for vertex_id, pos in vertex_positions.items():
            for neighbor_id in self.board.graph.get_neighbors(vertex_id):
                if neighbor_id > vertex_id:
                    color = self.board.graph.get_edge_color(vertex_id, neighbor_id)

                    if color is not None:
                        pos_x, pos_y = pos
                        neighbor_pos_x, neighbor_pos_y = vertex_positions[neighbor_id]
                        
                        new_x = (pos_x + neighbor_pos_x) // 2
                        new_y = (pos_y + neighbor_pos_y) // 2

                        road = Road(color, (new_x, new_y))
                        angle = -math.degrees(math.atan2(neighbor_pos_y - pos_y, neighbor_pos_x - pos_x))

                        assert road.image is not None
                        assert road.rect is not None
                        scaled = pygame.transform.scale(road.image, (road_size[0], road_size[1]))
                        rotated = pygame.transform.rotate(scaled, angle)
                        road.image = rotated
                        road.rect = rotated.get_rect(center=road.rect.topleft)

                        road_sprites.append(road)
        
        return road_sprites

    def update_robber(self, hex_sprites: list[Hex], token_size: int, token_spacing: list[int]) -> Token | None:
        ''' Creates new robber sprite. Robber is placed at the regular token offset based on the hex position. '''
        robber = None
        
        for sprite in hex_sprites:
                if self.board.robber_placement == sprite.id:
                        assert sprite.rect is not None
                        robber = self._create_robber(token_size, sprite.rect.x + token_spacing[0], sprite.rect.y + token_spacing[1])

        return robber
    
    def update_buildings(self, building_size: int, vertex_positions: dict) -> list[Structure]:
        ''' Creates new building sprites. Positioning based entirely on vertex positions dict.'''
        building_sprites = []

        for i, building in self.board.structures.items():

            if building != (None, None):
                building_type, color = building
                pos_x, pos_y = vertex_positions[i]
                building_sprite = Structure(color, building_type, (pos_x, pos_y))

                assert building_sprite.image is not None
                assert building_sprite.rect is not None
                scaled = pygame.transform.scale(building_sprite.image, (building_size, building_size))
                building_sprite.image = scaled
                building_sprite.rect = scaled.get_rect(center=(pos_x, pos_y))

                building_sprites.append(building_sprite)

        return building_sprites

    def _create_robber(self, token_size: int, pos_x: float | int, pos_y: float | int) -> Token:
        ''' Creates and returns new robber token. '''
        new_robber = Token(7, (pos_x, pos_y))

        assert new_robber.image is not None
        assert new_robber.rect is not None
        scaled = pygame.transform.scale(new_robber.image, (token_size, token_size))
        new_robber.image = scaled
        new_robber.rect = scaled.get_rect(topleft=new_robber.rect.topleft)

        return new_robber