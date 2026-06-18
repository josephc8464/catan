import pygame

class HexRenderer:
    def __init__(self, target_hex_size):
        self.target_hex_size = target_hex_size
        
        self.tile_images = {
            'wood':   pygame.transform.scale(pygame.image.load("graphics/default/hexes/wood.png"),   (self.target_hex_size, self.target_hex_size)),
            'brick':  pygame.transform.scale(pygame.image.load("graphics/default/hexes/brick.png"),  (self.target_hex_size, self.target_hex_size)),
            'sheep':  pygame.transform.scale(pygame.image.load("graphics/default/hexes/sheep.png"),  (self.target_hex_size, self.target_hex_size)),
            'wheat':  pygame.transform.scale(pygame.image.load("graphics/default/hexes/wheat.png"),  (self.target_hex_size, self.target_hex_size)),
            'ore':    pygame.transform.scale(pygame.image.load("graphics/default/hexes/ore.png"),    (self.target_hex_size, self.target_hex_size)),
            'desert': pygame.transform.scale(pygame.image.load("graphics/default/hexes/desert.png"), (self.target_hex_size, self.target_hex_size)),
        }
    
    def draw_hex(self, screen, tile, x, y):
        screen.blit(self.tile_images[tile.resource], (x, y))