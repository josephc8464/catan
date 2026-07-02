import pygame
from rendering.utils import ColorUtility

class Road(pygame.sprite.Sprite):
    road_image = None

    def __init__(self, color, pos):
        super().__init__()

        if self.road_image == None:
            self.load_images()

        self.image = self._get_color_road(color)
        self.rect = self.image.get_rect(topleft=pos)
    
    @classmethod
    def load_images(cls):
        cls.road_image = pygame.image.load("graphics/default/buildings/road_icon.png").convert_alpha()

    def _get_color_road(self, color):
        color_util = ColorUtility()

        assert Road.road_image is not None
        road_image = Road.road_image.copy()
        road_image.fill(color_util.get_color(color), special_flags=pygame.BLEND_RGB_MULT)
        return road_image
