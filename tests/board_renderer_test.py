import random
import pygame
import sys
sys.path.append('.')

from rendering.default_board_renderer import DefaultBoardRenderer
from game.board_presets.default_board import DefaultBoard

def board_renderer_test(board, frames=None):
    pygame.init()
    clock = pygame.time.Clock()
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
        clock.tick(60)
    
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

def board_random_game():
    board = DefaultBoard()
    board.setup_board()

    colors = ["red", "blue", "green", "purple"]
    building_types = ["settlement", "city"]
    
    for vertex_id in range(54):
        if random.random() < 0.5:  # 50% chance a vertex has a building
            color = random.choice(colors)
            building_type = random.choice(building_types)
            board.add_building(vertex_id, color, building_type)

    for (u, v) in list(board.graph.edge_color.keys()):
        if u < v and random.random() < 0.5:  # 50% chance an edge has a road
            color = random.choice(colors)
            board.graph.set_edge_color(u, v, color)

    board_renderer_test(board)

def board_full_test():
    tests = [
        board_no_settlements_or_roads,
        board_all_roads,
        board_all_settlements,
        board_all_cities,
        board_all_roads_settlements,
        board_all_roads_cities,
        board_random_game,
    ]
    for test in tests:
        test()


if __name__ == "__main__":
    board_full_test()