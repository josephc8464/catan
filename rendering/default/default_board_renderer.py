import pygame
from rendering.default.renderer_components import HexRenderer, RoadRenderer, TokenRenderer, PortRenderer, BuildingRenderer

class DefaultBoardRenderer:
    def __init__(self, screen):
        scale = screen.height / 1080
        self.target_scale = 125
        self.target_hex_size = int(self.target_scale * scale)
        self.hex_spacing_x = int(self.target_hex_size * 0.70)
        self.hex_spacing_y = int(self.target_hex_size * 0.95)

        token_offset_x = int(self.target_hex_size * 0.3375)
        token_offset_y = int(self.target_hex_size * 0.3)
        token_size = int(self.target_scale * 0.32 * scale)
        building_size = int(25 * scale)
        
        self.token_renderer = TokenRenderer(token_offset_x, token_offset_y, token_size)
        self.building_renderer = BuildingRenderer(building_size, self.target_hex_size)
        self.hex_renderer = HexRenderer(self.target_hex_size)
        self.road_renderer = RoadRenderer(self.target_hex_size)

    def draw(self, screen, board):
        tiles = board.tiles
        hex_column_sizes = [3, 4, 5, 4, 3]

        total_width = len(hex_column_sizes) * self.hex_spacing_x
        total_height = max(hex_column_sizes) * (self.hex_spacing_y / 2)

        x = (screen.width - total_width) / 2
        y = (screen.height - total_height) / 2.25
        index = 0

        for i in range(len(hex_column_sizes)):
            for j in range(hex_column_sizes[i]):
                self.hex_renderer.draw_hex(screen, tiles[index], x, y + self.hex_spacing_y * j)
                self.token_renderer.draw_token(screen, board, tiles[index], x, y + self.hex_spacing_y * j)
                self.road_renderer.draw_roads(screen, board, tiles[index], x, y + self.hex_spacing_y * j)
                self.building_renderer.draw_buildings(screen, board, tiles[index], x, y + self.hex_spacing_y * j)

                index += 1
            x += self.hex_spacing_x
            if len(hex_column_sizes) - i - 1 > 0:
                y -= (hex_column_sizes[i+1] - hex_column_sizes[i]) * (self.hex_spacing_y / 2)


