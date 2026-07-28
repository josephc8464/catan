from dataclasses import dataclass
import pytest

from game.game_controller import GameController
from game.player import Player
from game.turn_manager import TurnManager
from game.board_presets.default.default_board import DefaultBoard
from game.board_presets.default.board_context import BoardContext


@dataclass
class GameSetup:
    """Strongly typed container for game integration test fixtures."""
    controller: GameController
    board: DefaultBoard
    p1: Player
    p2: Player
    p3: Player
    p4: Player
    tm: TurnManager
    context: BoardContext


@pytest.fixture
def game() -> GameSetup:
    """Provides a fully wired real-game environment."""
    board = DefaultBoard()
    board.setup_board()

    p1 = Player('Alice', 'red')
    p2 = Player('Bob', 'blue')
    p3 = Player('Eve', 'green')
    p4 = Player('Joseph', 'purple')
    players = [p1, p2, p3, p4]

    tm = TurnManager(players)
    context = BoardContext()
    controller = GameController(board, players, tm, context)
    
    return GameSetup(
        controller=controller,
        board=board,
        p1=p1, p2=p2, p3=p3, p4=p4,
        tm=tm,
        context=context
    )

def subtract_resources(inventory: dict[str, int], cost: dict[str, int]) -> dict[str, int]:
    """Returns a new dict representing inventory minus cost."""
    return {res: amt - cost.get(res, 0) for res, amt in inventory.items()}


def assert_paid(game: GameSetup, player: Player, start_res: dict[str, int], item: str):
    cost = game.context.get_cost(item)
    assert player.resources == subtract_resources(start_res, cost)

def assert_not_paid(player: Player, start_res: dict[str, int]):
    assert player.resources == start_res