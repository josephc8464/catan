import math

import pygame
from rendering.default.board_renderer_components.sprites import Token, Road, Building, road
from rendering.utils import ColorUtility, PositionUtility

class DynamicSpriteManager():
    def __init__(self):
        self._load_sprite_images()
        
        self.pos_util = PositionUtility()
        self.color_util = ColorUtility()
    
    def _load_sprite_images(self):
        Token.load_images()
        Road.load_images()
        Building.load_images()

    def update_roads(self, board, vertex_positions, road_size) -> list[Road]:
        road_sprites = []

        for vertex_id, pos in vertex_positions.items():
            for neighbor_id in board.graph.get_neighbors(vertex_id):
                if neighbor_id > vertex_id:
                    color = board.graph.get_edge_color(vertex_id, neighbor_id)

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

    def update_robber(self, board, hex_sprites, token_size, token_spacing) -> Token | None:
        robber = None

        for sprite in hex_sprites:
                if board.robber_placement == sprite.id:
                        robber = self._create_robber(token_size, sprite.rect.x + token_spacing[0], sprite.rect.y + token_spacing[1])

        return robber
    
    def update_buildings(self, board, building_size, vertex_positions) -> list[Building]:
        building_sprites = []

        for i, building in board.buildings.items():
            if building is not None:
                building_type, color = building
                pos_x, pos_y = vertex_positions[i]
                building_sprite = Building(color, building_type, (pos_x, pos_y))

                assert building_sprite.image is not None
                assert building_sprite.rect is not None
                scaled = pygame.transform.scale(building_sprite.image, (building_size, building_size))
                building_sprite.image = scaled
                building_sprite.rect = scaled.get_rect(center=(pos_x, pos_y))

                building_sprites.append(building_sprite)

        return building_sprites

    def _create_robber(self, token_size, pos_x, pos_y) -> Token:
        new_robber = Token(7, (pos_x, pos_y))

        assert new_robber.image is not None
        assert new_robber.rect is not None
        scaled = pygame.transform.scale(new_robber.image, (token_size, token_size))
        new_robber.image = scaled
        new_robber.rect = scaled.get_rect(topleft=new_robber.rect.topleft)

        return new_robber