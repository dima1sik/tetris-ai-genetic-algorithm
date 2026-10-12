import pytest

from ai.bot import Bot
from core.board import Board
from core.game import Game
from core.piece import Piece


def test_bot_weights_are_owned_and_empty_weights_are_respected():
    first, second = Bot(), Bot()
    first.weights["holes"] = 100
    assert second.weights["holes"] == -4
    supplied = {"holes": -1}
    bot = Bot(supplied)
    supplied["holes"] = 999
    assert bot.weights == {"holes": -1}
    assert Bot({}).evaluate_board({"holes": 3}) == 0


@pytest.mark.parametrize("weights", [{"holes": float("nan")}, {"holes": float("inf")}, {"holes": "-4"}, {"unknown": 1}])
def test_invalid_weights_are_rejected(weights):
    with pytest.raises(ValueError):
        Bot(weights)


@pytest.mark.parametrize("move", [{"x": -10, "rotation_index": 0}, {"x": 0}, {"x": "0", "rotation_index": 0}, {"x": 0, "rotation_index": 0, "piece": "unknown"}])
def test_invalid_bot_move_leaves_game_unchanged(move):
    game = Game()
    before = (game.board.copy().grid, game.current_piece, game.current_x, game.current_y, game.score, game.lines)
    with pytest.raises(ValueError):
        game.apply_bot_move(move)
    assert (game.board.grid, game.current_piece, game.current_x, game.current_y, game.score, game.lines) == before


def test_bot_simulation_matches_applied_line_clearing_move():
    game = Game()
    game.current_piece = Piece("I")
    game.board.grid[-1] = [0, 0, 0, 0, 1, 1, 1, 1, 1, 1]
    bot = Bot({"lines_cleared": 1})
    move = bot.find_best_move(game.board, game.current_piece)
    simulated, cleared = game.board.simulate_place(Piece("I", move["rotation_index"]), move["x"])
    assert cleared == 1
    assert game.apply_bot_move(move)
    assert game.board.grid == simulated.grid
    assert game.lines == 1
    assert game.score == 100


def test_bot_can_plan_from_current_height_without_invalid_lock():
    game = Game()
    game.current_piece = Piece("O")
    game.current_y = 5
    game.board.grid[5][0] = 7
    before = game.board.copy().grid
    with pytest.raises(ValueError):
        game.apply_bot_move({"rotation_index": 0, "x": 0})
    assert game.board.grid == before
    bot = Bot()
    move = bot.find_best_move(game.board, game.current_piece, start_y=game.current_y)
    simulated, _ = game.board.simulate_place(Piece("O", move["rotation_index"]), move["x"], start_y=game.current_y)
    game.apply_bot_move(move)
    assert game.board.grid == simulated.grid


def test_no_legal_move_does_not_mutate_the_board():
    board = Board()
    board.grid = [[1] * board.WIDTH for _ in range(board.HEIGHT)]
    before = board.copy().grid
    assert Bot().find_best_move(board, Piece("O")) is None
    assert board.grid == before
