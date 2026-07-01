import pygame
from rendering.default.board_renderer_components.sprites import Hex, Token, Port
from rendering.utils import ColorUtility, PositionUtility

class StaticSpriteLoader():
    def __init__(self):
        self._load_sprite_images()

        self.pos_util = PositionUtility()
        self.color_util = ColorUtility()
    
    def _load_sprite_images(self):
        Hex.load_images()
        Token.load_images()
        Port.load_images()
    
    def calculate_vertex_positions(self, tile_vertices, hex_sprites, hex_spacing) -> dict[int, tuple[float, float]]:
        vertex_positions = {i: (0.0, 0.0) for i in range(54)}
        
        for hex in hex_sprites:
            tile_verts = tile_vertices[hex.id]
            for vertex in tile_verts:

                if vertex_positions[vertex] != (0.0, 0.0):
                    continue

                pos_offset = self.pos_util.get_vertex_offset(tile_verts, vertex)
                pos_offset_x = pos_offset[0]
                pos_offset_y = pos_offset[1]

                pos_x_scaled = hex.rect.x + (pos_offset_x * hex_spacing[0])
                pos_y_scaled = hex.rect.y + (pos_offset_y * hex_spacing[1])

                vertex_positions[vertex] = (pos_x_scaled, pos_y_scaled)

        return vertex_positions

    def _add_hex_sprite(self, hex_size, resource, hex_index, pos_x, pos_y) -> Hex:
        hex = Hex(resource, (pos_x, pos_y ), hex_index)
        
        assert hex.image is not None
        assert hex.rect is not None
        scaled = pygame.transform.scale(hex.image, (hex_size, hex_size))
        hex.image = scaled
        hex.rect = scaled.get_rect(topleft=hex.rect.topleft)

        return hex


    def _add_token_sprite(self, token_size, number, pos_x, pos_y) -> Token | None:
        token = None

        if number is not None:
            #Create Sprite
            token = Token(number, (pos_x, pos_y))

            assert token.image is not None
            assert token.rect is not None
            scaled = pygame.transform.scale(token.image, (token_size, token_size))
            token.image = scaled
            token.rect = scaled.get_rect(topleft=token.rect.topleft)
        
        return token
    
    def _add_port_sprite(self, board, hex_spacing, port_size, hex_index, pos_x, pos_y) -> Port | None:
        tile_vertices = board.tile_vertices[hex_index]
        port = None

        for (v1, v2) in board.ports.keys():
            #Determine if tile has a port
            if v1 in tile_vertices and v2 in tile_vertices:
                
                #Create Sprite
                resource = board.ports[(v1, v2)]
                orientation = self.pos_util.determine_orientation(tile_vertices, v1, v2)
                offset = self.pos_util.get_port_offset(orientation)

                new_pos_x = pos_x + offset[0] * hex_spacing[0]
                new_pos_y = pos_y + offset[1] * hex_spacing[1]
                port = Port(resource,(new_pos_x, new_pos_y ))

                assert port.image is not None
                assert port.rect is not None
                scaled = pygame.transform.scale(port.image, (port_size, port_size))
                port.image = scaled
                port.rect = scaled.get_rect(topleft=port.rect.topleft)

        return port   

    def load_static_sprites(self, board, land_hex_columns, sprite_config) -> tuple[list, list, list]:
        hex_size = sprite_config["hex_size"]
        token_size = sprite_config["token_size"]
        port_size = sprite_config["port_size"]
        hex_spacing = sprite_config["hex_spacing"]
        token_spacing = sprite_config["token_spacing"]

        hex_sprites = []
        token_sprites = []
        port_sprites = []
        
        hex_index = 0
        
        #Land Position Offset
        land_pos_y = -hex_spacing[1] // 10 - hex_spacing[1] // 2
        land_pos_x = (-hex_spacing[0] // 2) + (hex_spacing[0] * 11)
        
        #Land Hexes Y Adjustment
        y_adjust = 0

        #Land Hexes occur at the middle of the board (11 - 15)
        for i in range(5):
            land_hex_index = i

            #Add land sprites by column
            for j in range(land_hex_columns[land_hex_index]):
                pos_x = land_pos_x + hex_spacing[0] * i
                pos_y = land_pos_y + y_adjust + hex_spacing[1] * (j + 5)

                port_pos_x = pos_x + hex_spacing[0] // 4 
                port_pos_y = pos_y + hex_spacing[1] // 4
                
                hex_sprite = self._add_hex_sprite(hex_size, board.tiles[hex_index].resource, hex_index, pos_x, pos_y)
                token_sprite = self._add_token_sprite(token_size, board.tiles[hex_index].number, (pos_x + token_spacing[0]), (pos_y + token_spacing[1]))
                port_sprite = self._add_port_sprite(board, hex_spacing, port_size, hex_index, port_pos_x, port_pos_y)

                if hex_sprite is not None:
                    hex_sprites.append(hex_sprite)
                
                if token_sprite is not None:
                    token_sprites.append(token_sprite)
                
                if port_sprite is not None:
                    port_sprites.append(port_sprite)
                
                hex_index += 1                    

            #Adjust hex_y for stagger (land hexes)
            if len(land_hex_columns) - land_hex_index - 1 > 0:
                y_adjust -= (land_hex_columns[land_hex_index+1] - land_hex_columns[land_hex_index]) * (hex_spacing[1] // 2)

        return hex_sprites, token_sprites, port_sprites
    
    def load_background(self, window_res, hex_size, hex_spacing) -> pygame.Surface:
        sea_image = pygame.transform.scale(Hex.images['sea'], (hex_size, hex_size))

        #Sea Hexes Initial Start Position
        initial_posx = -hex_spacing[0] // 2
        initial_posy = -hex_spacing[1] // 10
        
        #Background Surface Setup
        background = pygame.Surface((window_res[0]*2, window_res[1]*2), pygame.SRCALPHA)
        background.fill((65, 167, 204))

        #28 x 14 sea hexes to fill the background at max zoom
        for i in range(28):
            for j in range(14):
                
                #Sea Hexes fill the whole board
                pos = (initial_posx + hex_spacing[0] * i, initial_posy + hex_spacing[1] * j )
                background.blit(sea_image, pos)

            #Alternating Hex Stagger
            if i % 2 == 0:
                initial_posy -= hex_spacing[1] // 2
            else:
                initial_posy += hex_spacing[1] // 2

        return background