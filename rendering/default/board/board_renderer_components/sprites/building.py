import pygame
from rendering.utils import ColorUtility

class Building(pygame.sprite.Sprite):
    images = {}

    def __init__(self, color, building_type, pos):
        super().__init__()

        if self.images == None:
            self.load_images()

        self.image = self._get_color_building(color, building_type)
        self.rect = self.image.get_rect(topleft=pos)
    
    @classmethod
    def load_images(cls):
        cls.images = {
            'settlement': pygame.image.load("graphics/default/buildings/settlement_icon.png").convert_alpha(),
            'city': pygame.image.load("graphics/default/buildings/city_icon.png").convert_alpha()
        }

    def _get_color_building(self, color, building_type):
        color_util = ColorUtility()
        image = Building.images[building_type].copy()
        image.fill(color_util.get_color(color), special_flags=pygame.BLEND_RGB_MULT)
        return image
