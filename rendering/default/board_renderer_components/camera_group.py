import pygame

class CameraGroup(pygame.sprite.Group): 
    display_surface: pygame.Surface

    def __init__(self, window_resolution, display_surface, scale):
        super().__init__()
        self.display_surface = display_surface
        self.display_surface_w = self.display_surface.get_width()
        self.display_surface_h = self.display_surface.get_height()

        self.background = pygame.Surface((window_resolution[0], window_resolution[1]), pygame.SRCALPHA)

        #camera offset
        self.offset = pygame.math.Vector2()
        self.half_w = self.display_surface_w // 2
        self.half_h = self.display_surface_h // 2

        #zoom
        self.zoom_scale = 1
        self.internal_surf_size = (window_resolution[0]*2, window_resolution[1]*2)
        self.internal_surf = pygame.Surface(self.internal_surf_size, pygame.SRCALPHA)
        self.internal_rect = self.internal_surf.get_rect(center = (self.half_w, self.half_h))
        self.internal_surface_size_vector = pygame.math.Vector2(self.internal_surf_size)
        self.internal_offset = pygame.math.Vector2()
        self.internal_offset.x = self.internal_surf_size[0] // 2 - self.half_w
        self.internal_offset.y = self.internal_surf_size[1] // 2 - self.half_h

    def update_zoom(self, zoom_scale, mouse_pos):
        max_zoom_in = 2.5
        max_zoom_out = 0.5

        old_zoom = self.zoom_scale
        
        if zoom_scale > 0:
            self.zoom_scale = min(max_zoom_in, zoom_scale+self.zoom_scale)
        else:
            self.zoom_scale = max(max_zoom_out, zoom_scale+self.zoom_scale)
        
        zoom_ratio = self.zoom_scale / old_zoom

        if zoom_ratio > 1:
            self.internal_offset.x = mouse_pos[0] - (mouse_pos[0] - self.internal_offset.x) * zoom_ratio
            self.internal_offset.y = mouse_pos[1] - (mouse_pos[1] - self.internal_offset.y) * zoom_ratio
        elif zoom_ratio < 1:
            self.internal_offset.x += (self.half_w - self.internal_offset.x) * (0.45)
            self.internal_offset.y += (self.half_h - self.internal_offset.y) * (0.45)
        
        if self.zoom_scale <= max_zoom_out:
            self.internal_offset.x = self.half_w
            self.internal_offset.y = self.half_h

    def custom_draw(self):
        mouse_pos = pygame.mouse.get_pos()

        if self.background:
            self.internal_surf.blit(self.background, (0, 0))
        
        for sprite in self.sprites():
            self.internal_surf.blit(sprite.image, sprite.rect.topleft)

        scaled_surf = pygame.transform.scale(self.internal_surf,self.internal_surface_size_vector * self.zoom_scale)
        scaled_rect = scaled_surf.get_rect(center = (self.internal_offset.x, self.internal_offset.y))
        
        self.display_surface.blit(scaled_surf,scaled_rect)