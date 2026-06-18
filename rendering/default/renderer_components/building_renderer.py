import pygame
from rendering.utils.color_utils import ColorUtility

class BuildingRenderer:

    def __init__(self, building_size, target_hex_size):

        self.ColorUtility = ColorUtility()
        self.building_size = building_size
        self.target_hex_size = target_hex_size
        
        self.indexHexPosition = {
            0: "topLeft",
            1: "topRight",
            2: "left",
            3: "right",
            4: "bottomLeft",
            5: "bottomRight"
        }

        self.building_offsets = {
            "topLeft":     (0.15, -0.15),
            "topRight":    (0.65, -0.15),
            "left":        (-0.05, 0.33),
            "right":       (0.85, 0.33),
            "bottomRight": (0.65, 0.8),
            "bottomLeft":  (0.15, 0.8),
        }

        self.building_images = {
            "settlement": pygame.transform.scale(pygame.image.load("graphics/default/buildings/settlement.png"), (self.building_size, self.building_size)),
            "city":       pygame.transform.scale(pygame.image.load("graphics/default/buildings/city.png"), (self.building_size, self.building_size))
        }

    
    def determine_building_vertex(self, board, tile, targetVertex) -> str:
        for i, vertex in enumerate(board.tile_vertices[tile.tile_id]):
            if vertex == targetVertex:
                index = i
        
        return self.indexHexPosition[index]

    def draw_buildings(self, screen, board, tile, x, y):
        for vertex in board.tile_vertices[tile.tile_id]:
            if vertex in board.buildings and board.buildings[vertex] != None:
                orientation = self.determine_building_vertex(board, tile, vertex)
                self.draw_building_image(screen, board, vertex, orientation, x, y)
    
    def get_building_image(self, board, vertex):
        building = board.buildings[vertex]
        
        if building is None:
            return None
        
        building_type, color = building

        image = self.building_images[building_type].copy()
        image.fill(self.ColorUtility.get_color(color), special_flags=pygame.BLEND_RGBA_MULT)

        return image
    
    def draw_building_image(self, screen, board, vertex, orientation, x, y):
        image = self.get_building_image(board, vertex)
            
        x_frac, y_frac = self.building_offsets[orientation]
        xNew = x + int(self.target_hex_size * x_frac)
        yNew = y + int(self.target_hex_size * y_frac)
        
        screen.blit(image, (xNew, yNew))
