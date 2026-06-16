import pygame
import sys
sys.path.append('.')

from rendering.default_board_renderer import DefaultBoardRenderer
from game.board_presets.default_board import DefaultBoard

def board_renderer_test(board):
    pygame.init()
    screen = pygame.display.set_mode((1920, 1080), pygame.RESIZABLE)
    
    renderer = DefaultBoardRenderer(screen)
    
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
        
        screen.fill((0, 0, 0))
        renderer.draw(screen, board)
        pygame.display.flip()
    
    pygame.quit()

def board_no_settlements_or_roads():
    board = DefaultBoard()
    board.setup_board()

    board_renderer_test(board)


def color_all_roads(board, color="red"):
    for (u, v) in list(board.graph.edge_color.keys()):
        if u < v:
            board.graph.set_edge_color(u, v, color)

def board_all_roads():
    board = DefaultBoard()
    board.setup_board()
    
    color_all_roads(board, "red")

    board_renderer_test(board)

def build_all_buildings(board, type="settlement", color="red"):
    for i in range(54):
        board.buildings[i] = (type, color)

def board_all_settlements():
    board = DefaultBoard()
    board.setup_board()

    build_all_buildings(board)

    board_renderer_test(board)

def board_all_cities():
    board = DefaultBoard()
    board.setup_board()

    build_all_buildings(board, "city")

    board_renderer_test(board)

def board_all_roads_settlements():
    board = DefaultBoard()
    board.setup_board()

    build_all_buildings(board, "settlement")
    color_all_roads(board)

    board_renderer_test(board)

def board_all_roads_cities():
    board = DefaultBoard()
    board.setup_board()

    build_all_buildings(board, "city")
    color_all_roads(board)

    board_renderer_test(board)    

if __name__ == "__main__":
    board_all_roads_cities()