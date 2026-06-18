import pygame
from rendering.utils.color_utils import ColorUtility

class RoadRenderer:
    
    def __init__(self, target_hex_size):
        self.ColorUtility = ColorUtility()

        self.road_offsets = {
            "topCenter":    (0.35, 0.0175, 0.65, 0.0175),
            "topLeft":      (0.225, 0.1, 0.07, 0.425),
            "topRight":     (0.775, 0.1, 0.93, 0.425),
            "bottomCenter": (0.35, 0.9825, 0.65, 0.9825),
            "bottomLeft":   (0.225, 0.9, 0.07, 0.575),
            "bottomRight":  (0.775, 0.9, 0.93, 0.575),
        }
        self.target_hex_size = target_hex_size
    
    def draw_roads(self, screen, board, tile, x, y):
        for vertex1 in board.tile_vertices[tile.tile_id]:
            for vertex2 in board.tile_vertices[tile.tile_id]:
                if vertex1 < vertex2:
                    color = board.graph.get_edge_color(vertex1, vertex2)

                    if color is not None:
                        self.draw_color_line(screen, x, y, color, self.determine_orientation(board.tile_vertices[tile.tile_id], vertex1, vertex2))
    
    def draw_color_line(self, screen, x, y, color, orientation):
        road_width = int(self.target_hex_size * 0.05)
        
        rgb = self.ColorUtility.get_color(color)

        x1_frac, y1_frac, x2_frac, y2_frac = self.road_offsets[orientation]
        x1 = x + int(self.target_hex_size * x1_frac)
        x2 = x + int(self.target_hex_size * x2_frac)
        y1 = y + int(self.target_hex_size * y1_frac)
        y2 = y + int(self.target_hex_size * y2_frac)

        pygame.draw.line(screen, rgb, (x1, y1), (x2, y2), road_width)
    
    def determine_orientation(self, tile_vertices, vertex1, vertex2) -> str:
        for i, vertex in enumerate(tile_vertices):
            if vertex == vertex1:
                index1 = i
            
            if vertex == vertex2:
                index2 = i

        if index1 < 2:
            if index2 - index1 == 1:
                return "topCenter"
            elif index2 == 2:
                return "topLeft"
            else:
                return "topRight"
        elif index1 < 4:
            if index1 == 2:
                return "bottomLeft"
            else:
                return "bottomRight"
        else:
            return "bottomCenter"