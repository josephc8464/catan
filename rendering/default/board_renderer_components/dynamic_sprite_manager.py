import pygame
from rendering.default.board_renderer_components.sprites import Token, Road, Building
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

    def update_roads(self, board, hex_sprites, road_size, hex_spacing) -> list[Road]:
        road_sprites = []

        for sprite in hex_sprites:
            roads = self._draw_hex_roads(board, board.tile_vertices[sprite.id], road_size, hex_spacing, sprite.rect.x, sprite.rect.y)
            road_sprites.extend(roads)
        
        return road_sprites

    def update_robber(self, board, hex_sprites, token_size, token_spacing) -> Token | None:
        robber = None

        for sprite in hex_sprites:
                if board.robber_placement == sprite.id:
                        robber = self._create_robber(token_size, sprite.rect.x + token_spacing[0], sprite.rect.y + token_spacing[1])

        return robber
    
    def update_buildings(self, board, hex_sprites, building_size, hex_spacing) -> list[Building]:
        building_sprites = []

        for sprite in hex_sprites:
            buildings = self._draw_hex_buildings(board, board.tile_vertices[sprite.id], building_size, hex_spacing, sprite.rect.x, sprite.rect.y)
            building_sprites.extend(buildings)

        return building_sprites
    
    def _draw_hex_buildings(self, board, tile_verts, build_size, hex_spacing, pos_x, pos_y) -> list[Building]:
        sprites = []
        for vertex in tile_verts:
            building = board.buildings[vertex]

            if building is None:
                continue

            building_type, color = building
            pos_offset = self.pos_util.get_building_offset(tile_verts, vertex)
            pos_offset_x = pos_offset[0]
            pos_offset_y = pos_offset[1]

            pos_x_scaled = pos_x + (pos_offset_x * hex_spacing[0])
            pos_y_scaled = pos_y + (pos_offset_y * hex_spacing[1])

            building_sprite = Building(color, building_type, (pos_x_scaled, pos_y_scaled))

            assert building_sprite.image is not None
            building_sprite.image = pygame.transform.scale(building_sprite.image, (build_size, build_size))
            
            sprites.append(building_sprite)

        return sprites

    def _draw_hex_roads(self, board, tile_verts, road_size, hex_spacing, pos_x, pos_y) -> list[Road]:
        road_sprites = []

        for vertex1 in tile_verts:
            for vertex2 in tile_verts:
                if vertex1 < vertex2:
                    color = board.graph.get_edge_color(vertex1, vertex2)

                    if color is not None:
                        orientation = self.pos_util.determine_orientation(tile_verts, vertex1, vertex2)
                        offset = self.pos_util.get_road_offset(orientation)
                        new_pos_x = hex_spacing[0] * offset[0] + pos_x
                        new_pos_y = hex_spacing[1] * offset[1] + pos_y

                        road = self._draw_road(color, road_size, new_pos_x, new_pos_y, offset[2])
                        road_sprites.append(road)

        return road_sprites
    
    def _draw_road(self, color, road_size, pos_x, pos_y, angle) -> Road:
        road_sprite = Road(color, (pos_x, pos_y))

        assert road_sprite.image is not None
        scaled = pygame.transform.scale(road_sprite.image, (road_size[0], road_size[1]))
        rotated = pygame.transform.rotate(scaled, angle)
        road_sprite.image = rotated
        
        assert road_sprite.rect is not None
        road_sprite.rect = rotated.get_rect(topleft=road_sprite.rect.topleft)
        
        return road_sprite

    def _create_robber(self, token_size, pos_x, pos_y) -> Token:
        new_robber = Token(7, (pos_x, pos_y))

        assert new_robber.image is not None
        new_robber.image = pygame.transform.scale(new_robber.image, (token_size, token_size))

        return new_robber