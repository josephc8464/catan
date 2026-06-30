# Example file showing a basic pygame "game loop"
import pygame
from rendering.default.board_renderer import DefaultBoardRenderer
from game.board_presets.default_board import DefaultBoard

# pygame setup
pygame.init()
info = pygame.display.Info()
width = info.current_w
height = info.current_h
screen = pygame.display.set_mode((1280, 720), pygame.RESIZABLE)
pygame.window.Window
clock = pygame.time.Clock()
running = True

while running:

    # poll for events
    # pygame.QUIT event means the user clicked X to close your window
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
    

    # RENDER YOUR GAME HERE

    # flip() the display to put your work on screen
    pygame.display.flip()

    clock.tick(60)  # limits FPS to 60

pygame.quit()