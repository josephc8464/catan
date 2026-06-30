import pygame

class Token(pygame.sprite.Sprite):
    images = {}

    def __init__(self, token_number, pos):
        super().__init__()
        if not self.images:
            self.load_images()
        
        self.image = Token.images[token_number]
        self.rect = self.image.get_rect(topleft = pos)

    @classmethod
    def load_images(cls):
        cls.images = {
            2 : pygame.image.load('graphics/default/tokens/token_two.png').convert_alpha(),
            3 : pygame.image.load('graphics/default/tokens/token_three.png').convert_alpha(),
            4 : pygame.image.load('graphics/default/tokens/token_four.png').convert_alpha(),
            5 : pygame.image.load('graphics/default/tokens/token_five.png').convert_alpha(),
            6 : pygame.image.load('graphics/default/tokens/token_six.png').convert_alpha(),
            7 : pygame.image.load('graphics/default/tokens/token_robber.png').convert_alpha(),
            8 : pygame.image.load('graphics/default/tokens/token_eight.png').convert_alpha(),
            9 : pygame.image.load('graphics/default/tokens/token_nine.png').convert_alpha(),
            10 : pygame.image.load('graphics/default/tokens/token_ten.png').convert_alpha(),
            11 : pygame.image.load('graphics/default/tokens/token_eleven.png').convert_alpha(),
            12 : pygame.image.load('graphics/default/tokens/token_twelve.png').convert_alpha()
        }