import pygame
from rendering.default.board_renderer_components.sprites import Hex, Token, Port, Road, Building
from rendering.default.board_renderer_components import StaticSpriteLoader, DynamicSpriteManager, CameraGroup

class DefaultBoardRenderer():      
    def __init__(self, board, window_resolution, disaply_surface, scale):
        self.scale = scale

        #Dependencies
        self.camera_group = CameraGroup(window_resolution, disaply_surface, scale)
        self.static_loader = StaticSpriteLoader()
        self.dynamic_manager = DynamicSpriteManager()

        #Sprite Lists
        self.hex_sprites = []
        self.token_sprites = []
        self.port_sprites = []
        self.building_sprites = []
        self.road_sprites = []
        self.robber_sprite = None

        #Dirty Markers
        self.robber_dirty = True
        self.roads_dirty = True
        self.buildings_dirty = True

        #Hex Config
        self.hex_size = int(200 * self.scale)
        self.hex_spacing = [int(145 * self.scale), int(170 * self.scale)]

        #Token Config
        self.token_size = int(60 * self.scale)
        self.token_spacing = [int(self.hex_spacing[0] // 2), int(self.hex_spacing[1] // 1.75)]

        #Port Config
        self.port_size = int(125 * self.scale)

        #Road Config
        self.road_size = [int(80 * self.scale), int(20 * self.scale)]
        
        #Building Config
        self.building_size = int(50 * self.scale)

        sprite_config = {
            "hex_size": self.hex_size,
            "token_size": self.token_size,
            "port_size": self.port_size,
            "hex_spacing": self.hex_spacing,
            "token_spacing": self.token_spacing,
        }

        land_hex_columns = [3, 4, 5, 4, 3]
        self.camera_group.background = self.static_loader.load_background(window_resolution, self.hex_size, self.hex_spacing)
        self.hex_sprites, self.token_sprites, self.port_sprites = self.static_loader.load_static_sprites(board, land_hex_columns, sprite_config)
        self.camera_group.add(self.hex_sprites)
        self.camera_group.add(self.token_sprites)
        self.camera_group.add(self.port_sprites) 

    def render_board(self, board):
        
        if self.robber_dirty:
            self.robber_sprite = self.dynamic_manager.update_robber(board, self.hex_sprites, self.token_size, self.token_spacing)
            self.camera_group.add(self.robber_sprite)
            self.robber_dirty = False
        
        if self.roads_dirty:
            self._clear_sprites(self.road_sprites)
            self.road_sprites = self.dynamic_manager.update_roads(board, self.hex_sprites, self.road_size, self.hex_spacing)
            self.camera_group.add(self.road_sprites)
            self.roads_dirty = False

        if self.buildings_dirty:
            self._clear_sprites(self.building_sprites)
            self.building_sprites = self.dynamic_manager.update_buildings(board, self.hex_sprites, self.building_size, self.hex_spacing)
            self.camera_group.add(self.building_sprites)
            self.building_dirty = False
        
        self.camera_group.custom_draw()

    def _clear_sprites(self, sprite_list):
        for sprite in sprite_list:
            self.camera_group.remove(sprite)
        sprite_list.clear()