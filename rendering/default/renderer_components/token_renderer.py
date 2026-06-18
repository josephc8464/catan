import pygame

class TokenRenderer:
    def __init__(self, token_offset_x, token_offset_y, token_size):
        self.token_offset_x = token_offset_x
        self.token_offset_y = token_offset_y
        self.token_size = token_size

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
    
    def draw_token(self, screen, board, tile, x, y):

        token_pos = (x + self.token_offset_x, y + self.token_offset_y)

        if tile.resource != 'desert':
            screen.blit(self.token_images[tile.number], token_pos)
        
        if board.robber_placement == tile.tile_id:
            screen.blit(self.token_images[7], token_pos)