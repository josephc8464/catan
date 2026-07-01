import random
import pygame
import sys
sys.path.append('.')

from rendering.default.board_renderer import DefaultBoardRenderer
from game.board_presets.default_board import DefaultBoard

BASE_WIDTH, BASE_HEIGHT = 1920, 1080

def board_renderer_test(board):
    pygame.init()
    
    #Window Display Setup
    info = pygame.display.Info()

    screen_w, screen_h = info.current_w, info.current_h
    scale = min(screen_w / BASE_WIDTH, screen_h / BASE_HEIGHT)

    window_w = int(BASE_WIDTH * scale)
    window_h = int(BASE_HEIGHT * scale)
    
    screen = pygame.display.set_mode((window_w, window_h))

    #Renderer & Clock Init
    renderer = DefaultBoardRenderer(board, [window_w, window_h], screen, scale)
    clock = pygame.time.Clock()

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False

            if event.type == pygame.MOUSEWHEEL:
                renderer.camera_group.update_zoom(event.y * 0.075, pygame.mouse.get_pos())

            
        screen.fill((0, 0, 0))
        renderer.render_board(board)
        pygame.display.flip()
        clock.tick(60)
    
    pygame.quit()

def run_timed_test(board, frames=3):
    pygame.init()
    
    #Window Display Setup
    info = pygame.display.Info()

    screen_w, screen_h = info.current_w, info.current_h
    scale = min(screen_w / BASE_WIDTH, screen_h / BASE_HEIGHT)

    window_w = int(BASE_WIDTH * scale)
    window_h = int(BASE_HEIGHT * scale)

    screen = pygame.display.set_mode((window_w, window_h))

    #Renderer & Clock Init
    renderer = DefaultBoardRenderer(board, [window_w, window_h], screen, scale)
    clock = pygame.time.Clock()

    for _ in range(frames):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return
        
            if event.type == pygame.MOUSEWHEEL:
                renderer.camera_group.update_zoom(event.y * 0.075, pygame.mouse.get_pos())

        renderer.render_board(board)
        pygame.display.flip()
        clock.tick(1)  # 1 fps

    pygame.quit()

def board_no_settlements_or_roads(type_of_test=board_renderer_test):
    board = DefaultBoard()
    board.setup_board()

    type_of_test(board)


def color_all_roads(board, color="red"):
    for (u, v) in list(board.graph.edge_color.keys()):
        if u < v:
            board.graph.set_edge_color(u, v, color)

def board_all_roads(type_of_test=board_renderer_test):
    board = DefaultBoard()
    board.setup_board()
    
    color_all_roads(board, "red")

    type_of_test(board)

def build_all_buildings(board, type="settlement", color="red"):
    for i in range(54):
        board.buildings[i] = (type, color)

def board_all_settlements(type_of_test=board_renderer_test):
    board = DefaultBoard()
    board.setup_board()

    build_all_buildings(board)

    type_of_test(board)

def board_all_cities(type_of_test=board_renderer_test):
    board = DefaultBoard()
    board.setup_board()

    build_all_buildings(board, "city")

    type_of_test(board)

def board_all_roads_settlements(type_of_test=board_renderer_test):
    board = DefaultBoard()
    board.setup_board()

    build_all_buildings(board, "settlement")
    color_all_roads(board)

    type_of_test(board)

def board_all_roads_cities(type_of_test=board_renderer_test):
    board = DefaultBoard()
    board.setup_board()

    build_all_buildings(board, "city")
    color_all_roads(board)

    type_of_test(board) 

def board_random_game(type_of_test=board_renderer_test):
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

    type_of_test(board)

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
        test(run_timed_test)

if __name__ == "__main__":
    board_full_test()