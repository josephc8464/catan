from rendering.default.board.board_renderer_components import StaticSpriteLoader, DynamicSpriteManager, CameraGroup
from game.board_presets.default.default_board import DefaultBoard
from pygame import Surface

class DefaultBoardRenderer():    
    """
    Renderer built specifically for the DefaultBoard class.
    
    Recieves a DefaultBoard and processes the board by distributing work to the 
    related class. The DefaultBoardRenderer does not directly blit to the screen, but
    manages sprites and delegates which part of the board should be rendered based on input.
    
    Attributes:
        scale: Scales the sprites to match the target resolution on different display surfaces.
        board: The board to be rendered.

        camera_group: Blits sprites dependent on the zoom function.
        static_loader: Creates a surface to house static (unchanging) sprites. (used by camera_group)
        dynamic_manager: Manages the sprites that change. Reloads on updates. (used by camera_group)
        
        hex_sprites: Tracks the physical hex sprites contained on the board.
        token_sprites: Tracks the physical token sprites contained on the board. Excluding the robber/token 7.
        port_sprites: Tracks the physical port sprites contained on the board.
        port_bridge_sprites: Tracks the "port bridges" (pygame brown lines) contained on the board.
        building_sprites: Tracks settlement and city sprites contained on the board.
        road_sprites: Tracks road sprites contained on the board.
        robber_sprite: Tracks the robber sprite (token 7).

        robber_dirty: Dirty marker to reload on robber updates.
        roads_dirty: Dirty marker to reload on road updates.
        buildings_dirty: Dirty marker to reload on building updates (includes city and settlements).

        vertex_positions: Dictionary containing pixel coordinates of each vertex in the board. (vertices are the corners of the hexes)
        
        hex_size: Hex Sprite global scaling factor.
        hex_spacing: Contains the x and y offsets of hex sprites adjacent to one another.
        token_size: Token Sprite global scaling factor.
        token_spacing: Contains the x and y offsets of token sprites in relation to its Hex Sprite.
        port_size: Port Sprite global scaling factor.
        road_size: Road Sprite global scaling factor.
        building_size: Building Sprites global scaling factor (settlements and cities).

    """  
    def __init__(self, board: DefaultBoard, window_resolution: list[int], disaply_surface: Surface, scale: float):
        self.scale = scale
        self.board = board

        # --- Dependencies ---
        self.camera_group = CameraGroup(window_resolution, disaply_surface)
        self.static_loader = StaticSpriteLoader()
        self.dynamic_manager = DynamicSpriteManager(self.board)

        # --- Sprite Lists ---
        self.hex_sprites = []
        self.token_sprites = []
        self.port_sprites = []
        self.port_bridge_sprites = []
        self.building_sprites = []
        self.road_sprites = []
        self.robber_sprite = None

        # --- Dirty Markers ---
        self.robber_dirty = True
        self.roads_dirty = True
        self.buildings_dirty = True

        # --- Graph Positioning ---
        self.vertex_positions = {i: (0.0, 0.0) for i in range(54)}

        # --- Hex Config ---
        self.hex_size = int(200 * self.scale)
        self.hex_spacing = [int(145 * self.scale), int(170 * self.scale)]

        # --- Token Config ---
        self.token_size = int(60 * self.scale)
        self.token_spacing = [int(self.hex_spacing[0] // 2), int(self.hex_spacing[1] // 1.75)]

        # --- Port Config ---
        self.port_size = int(125 * self.scale)

        # --- Road Config ---
        self.road_size = [int(60 * self.scale), int(20 * self.scale)]
        
        # --- Building Config ---
        self.building_size = int(40 * self.scale)

        sprite_config = {
            "hex_size": self.hex_size,
            "token_size": self.token_size,
            "port_size": self.port_size,
            "hex_spacing": self.hex_spacing,
            "token_spacing": self.token_spacing,
        }

        # --- Land Hex Column Lengths (Traditional Catan) ---
        land_hex_columns = [3, 4, 5, 4, 3]
        
        # --- Creation of Init DefaultBoardRenderer Sprites ---
        self.camera_group.background = self.static_loader.load_background(window_resolution, self.hex_size, self.hex_spacing)
        self.hex_sprites, self.token_sprites, self.port_sprites = self.static_loader.load_static_sprites(self.board, land_hex_columns, sprite_config)
        self.vertex_positions = self.static_loader.calculate_vertex_positions(self.board.tile_vertices, self.hex_sprites, self.hex_spacing)
        self.port_bridge_sprites = self.static_loader.build_port_bridges(self.vertex_positions, self.port_sprites)

        # --- Init Sprites ---
        self.camera_group.add(self.hex_sprites)
        self.camera_group.add(self.token_sprites)
        self.camera_group.add(self.port_bridge_sprites)
        self.camera_group.add(self.port_sprites)

    def render_board(self):
        ''' Updates dynamic sprites on the board based on dirty markers. (Robber, Roads, Buildings)'''

        if self.robber_dirty:
            self.camera_group.remove(self.robber_sprite)
            self.robber_sprite = self.dynamic_manager.update_robber(self.hex_sprites, self.token_size, self.token_spacing)
            self.camera_group.add(self.robber_sprite)
            self.camera_group.dirty = True
            self.robber_dirty = False
        
        if self.roads_dirty:
            self._clear_sprites(self.road_sprites)
            self.road_sprites = self.dynamic_manager.update_roads(self.vertex_positions, self.road_size)
            self.camera_group.add(self.road_sprites)
            self.camera_group.dirty = True
            self.roads_dirty = False

        if self.buildings_dirty:
            self._clear_sprites(self.building_sprites)
            self.building_sprites = self.dynamic_manager.update_buildings(self.building_size, self.vertex_positions)
            self.camera_group.add(self.building_sprites)
            self.camera_group.dirty = True
            self.buildings_dirty = False
        
        self.camera_group.custom_draw()

    def _clear_sprites(self, sprite_list):
        ''' Clears a given sprite list from the camera_group and DefaultBoardRenderer. '''

        for sprite in sprite_list:
            self.camera_group.remove(sprite)
        sprite_list.clear()