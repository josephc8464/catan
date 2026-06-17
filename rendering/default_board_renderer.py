import pygame

class DefaultBoardRenderer:
    def __init__(self, screen):
        scale = screen.height / 1080
        self.target_scale = 125
        self.target_hex_size = int(self.target_scale * scale)
        self.token_size = int(self.target_scale * 0.32 * scale)
        self.building_size = int(25 * scale)
        
        self.hex_spacing_x = int(self.target_hex_size * 0.70)
        self.hex_spacing_y = int(self.target_hex_size * 0.95)
        self.token_offset_x = int(self.target_hex_size * 0.3375)
        self.token_offset_y = int(self.target_hex_size * 0.3)

        self.tile_images = {
            'wood':   pygame.transform.scale(pygame.image.load("graphics/default/hexes/wood.png"),   (self.target_hex_size, self.target_hex_size)),
            'brick':  pygame.transform.scale(pygame.image.load("graphics/default/hexes/brick.png"),  (self.target_hex_size, self.target_hex_size)),
            'sheep':  pygame.transform.scale(pygame.image.load("graphics/default/hexes/sheep.png"),  (self.target_hex_size, self.target_hex_size)),
            'wheat':  pygame.transform.scale(pygame.image.load("graphics/default/hexes/wheat.png"),  (self.target_hex_size, self.target_hex_size)),
            'ore':    pygame.transform.scale(pygame.image.load("graphics/default/hexes/ore.png"),    (self.target_hex_size, self.target_hex_size)),
            'desert': pygame.transform.scale(pygame.image.load("graphics/default/hexes/desert.png"), (self.target_hex_size, self.target_hex_size)),
        }

        self.token_images = {
            2:  pygame.transform.scale(pygame.image.load("graphics/default/tokens/token_2.png"),  (self.token_size, self.token_size)),
            3:  pygame.transform.scale(pygame.image.load("graphics/default/tokens/token_3.png"),  (self.token_size, self.token_size)),
            4:  pygame.transform.scale(pygame.image.load("graphics/default/tokens/token_4.png"),  (self.token_size, self.token_size)),
            5:  pygame.transform.scale(pygame.image.load("graphics/default/tokens/token_5.png"),  (self.token_size, self.token_size)),
            6:  pygame.transform.scale(pygame.image.load("graphics/default/tokens/token_6.png"),  (self.token_size, self.token_size)),
            7:  pygame.transform.scale(pygame.image.load("graphics/default/tokens/robber.png"),   (self.token_size, self.token_size)),
            8:  pygame.transform.scale(pygame.image.load("graphics/default/tokens/token_8.png"),  (self.token_size, self.token_size)),
            9:  pygame.transform.scale(pygame.image.load("graphics/default/tokens/token_9.png"),  (self.token_size, self.token_size)),
            10: pygame.transform.scale(pygame.image.load("graphics/default/tokens/token_10.png"), (self.token_size, self.token_size)),
            11: pygame.transform.scale(pygame.image.load("graphics/default/tokens/token_11.png"), (self.token_size, self.token_size)),
            12: pygame.transform.scale(pygame.image.load("graphics/default/tokens/token_12.png"), (self.token_size, self.token_size)),
        }

        self.building_images = {
            "settlement": pygame.transform.scale(pygame.image.load("graphics/default/buildings/settlement.png"), (self.building_size, self.building_size)),
            "city":       pygame.transform.scale(pygame.image.load("graphics/default/buildings/city.png"), (self.building_size, self.building_size))
        }

    def draw_hex(self, screen, board, tile, x, y):
        screen.blit(self.tile_images[tile.resource], (x, y))
                
        token_pos = (x + self.token_offset_x, y + self.token_offset_y)

        if tile.resource != 'desert':
            screen.blit(self.token_images[tile.number], token_pos)
        
        if board.robber_placement == tile.tile_id:
            screen.blit(self.token_images[7], token_pos)

    def draw_roads(self, screen, board, tile, x, y):
        for vertex1 in board.tile_vertices[tile.tile_id]:
            for vertex2 in board.tile_vertices[tile.tile_id]:
                if vertex1 < vertex2:
                    color = board.graph.get_edge_color(vertex1, vertex2)

                    if color is not None:
                        self.draw_color_line(screen, x, y, color, self.determine_orientation(board.tile_vertices[tile.tile_id], vertex1, vertex2))

    def determine_building_vertex(self, board, tile, targetVertex) -> str:
        for i, vertex in enumerate(board.tile_vertices[tile.tile_id]):
            if vertex == targetVertex:
                index = i
        
        match index:
            case 0:
                return "topLeft"
            case 1:
                return "topRight"
            case 2:
                return "left"
            case 3:
                return "right"
            case 4:
                return "bottomLeft"
            case 5:
                return "bottomRight" 

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
        image.fill(self.get_color(color), special_flags=pygame.BLEND_RGBA_MULT)

        return image
    
    def draw_building_image(self, screen, board, vertex, orientation, x, y):
        xDraw = x
        yDraw = y
        image = self.get_building_image(board, vertex)

        match orientation:
            case "topLeft":
                xDraw += int(self.target_hex_size*0.15)
                yDraw -= int(self.target_hex_size*0.15)
            case "topRight":
                xDraw += int(self.target_hex_size*0.65)
                yDraw -= int(self.target_hex_size*0.15)
            case "left":
                xDraw -= int(self.target_hex_size * 0.05)
                yDraw += int(self.target_hex_size  * 0.33)
            case "right":
                xDraw += int(self.target_hex_size * 0.85)
                yDraw += int(self.target_hex_size  * 0.33)
            case "bottomRight":
                xDraw += int(self.target_hex_size * 0.65)
                yDraw += int(self.target_hex_size  * 0.8)
            case "bottomLeft":
                xDraw += int(self.target_hex_size * 0.15)
                yDraw += int(self.target_hex_size  * 0.8)
            
        screen.blit(image, (xDraw, yDraw))

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

    def get_color(self, color):
        match color:
            case "red":
                return (255, 0, 0)
            case "blue":
                return (0, 0, 255)
            case "green":
                return (0, 165, 0)
            case "purple":
                return (255, 0, 255)
        
    def draw_color_line(self, screen, x, y, color, orientation):
        x1 = x
        x2 = x
        y1 = y
        y2 = y
        road_width = int(self.target_hex_size * 0.05)
        
        rgb = self.get_color(color)

        match orientation:
            case "topCenter":
                x1 += int(self.target_hex_size * 0.35)
                x2 += int(self.target_hex_size * 0.65)
                y1 += int(self.target_hex_size * 0.0175)
                y2 += int(self.target_hex_size * 0.0175)
            case "topLeft":
                x1 += int(self.target_hex_size * 0.225)
                x2 += int(self.target_hex_size * 0.07)
                y1 += int(self.target_hex_size * 0.1)
                y2 += int(self.target_hex_size * 0.425)
            case "topRight":
                x1 += int(self.target_hex_size * 0.775)
                x2 += int(self.target_hex_size * 0.93)
                y1 += int(self.target_hex_size * 0.1)
                y2 += int(self.target_hex_size * 0.425)
            case "bottomCenter":
                x1 += int(self.target_hex_size * 0.35)
                x2 += int(self.target_hex_size * 0.65)
                y1 += int(self.target_hex_size * 0.9825)
                y2 += int(self.target_hex_size * 0.9825)
            case "bottomLeft":
                x1 += int(self.target_hex_size * 0.225)
                x2 += int(self.target_hex_size * 0.07)
                y1 += int(self.target_hex_size * 0.9)
                y2 += int(self.target_hex_size * 0.575)
            case "bottomRight":
                x1 += int(self.target_hex_size * 0.775)
                x2 += int(self.target_hex_size * 0.93)
                y1 += int(self.target_hex_size * 0.9)
                y2 += int(self.target_hex_size * 0.575)

        pygame.draw.line(screen, rgb, (x1, y1), (x2, y2), road_width)

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
                self.draw_hex(screen, board, tiles[index], x, y + self.hex_spacing_y * j)
                self.draw_roads(screen, board, tiles[index], x, y + self.hex_spacing_y * j)
                self.draw_buildings(screen, board, tiles[index], x, y + self.hex_spacing_y * j)

                index += 1
            x += self.hex_spacing_x
            if len(hex_column_sizes) - i - 1 > 0:
                y -= (hex_column_sizes[i+1] - hex_column_sizes[i]) * (self.hex_spacing_y / 2)


