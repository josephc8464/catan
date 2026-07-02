import pygame

class Hex(pygame.sprite.Sprite):
    images = {}

    def __init__(self, tile_resource, pos, id):
        super().__init__()

        if not self.images:
            self.load_images()
        
        self.image = Hex.images[tile_resource]
        self.rect = self.image.get_rect(topleft = pos)
        self.id = id
    
    @classmethod
    def load_images(cls):
        cls.images = {
            'wood' : pygame.image.load('graphics/default/hexes/wood_hex.png').convert_alpha(),
            'brick' : pygame.image.load('graphics/default/hexes/brick_hex.png').convert_alpha(),
            'ore' : pygame.image.load('graphics/default/hexes/ore_hex.png').convert_alpha(),
            'sheep' : pygame.image.load('graphics/default/hexes/sheep_hex.png').convert_alpha(),
            'wheat' : pygame.image.load('graphics/default/hexes/wheat_hex.png').convert_alpha(),
            'sea' : pygame.image.load('graphics/default/hexes/sea_hex.png').convert_alpha(),
            'desert' : pygame.image.load('graphics/default/hexes/desert_hex.png').convert_alpha()
        }