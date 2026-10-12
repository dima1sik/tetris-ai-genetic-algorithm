from core.board import Board
from core.piece import Piece


def test_board_has_correct_size():
    board = Board()

    assert len(board.get_grid()) == 20
    assert len(board.get_grid()[0]) == 10


def test_can_place_piece_on_empty_board():
    board = Board()
    piece = Piece("O")

    assert board.can_place(piece, 0, 0) is True


def test_cannot_place_piece_outside_left_border():
    board = Board()
    piece = Piece("O")

    assert board.can_place(piece, -1, 0) is False


def test_cannot_place_piece_outside_right_border():
    board = Board()
    piece = Piece("O")

    assert board.can_place(piece, 9, 0) is False


def test_place_piece_marks_cells():
    board = Board()
    piece = Piece("O")

    board.place_piece(piece, 0, 0)

    grid = board.get_grid()

    assert grid[0][0] == 1
    assert grid[0][1] == 1
    assert grid[1][0] == 1
    assert grid[1][1] == 1


def test_clear_full_line():
    board = Board()

    board.grid[-1] = [1 for _ in range(board.WIDTH)]

    cleared = board.clear_lines()

    assert cleared == 1
    assert board.get_grid()[0] == [0 for _ in range(board.WIDTH)]
import pytest



@pytest.mark.parametrize("x,y", [(-1, 0), (9, 0), (0, -1), (0, 19)])
def test_invalid_placement_does_not_partially_write_board(x, y):
    board = Board()
    before = board.copy().grid
    with pytest.raises(ValueError):
        board.place_piece(Piece("O"), x, y)
    assert board.grid == before


def test_collision_does_not_overwrite_locked_cells():
    board = Board()
    board.grid[0][0] = 7
    before = board.copy().grid
    with pytest.raises(ValueError):
        board.place_piece(Piece("O"), 0, 0)
    assert board.grid == before


def test_clearing_multiple_lines_preserves_surviving_row_order():
    board = Board()
    board.grid[-4][0] = 2
    board.grid[-3] = [1] * board.WIDTH
    board.grid[-2][1] = 3
    board.grid[-1] = [1] * board.WIDTH
    assert board.clear_lines() == 2
    assert board.grid[-2][0] == 2
    assert board.grid[-1][1] == 3
    assert board.grid[:2] == [[0] * board.WIDTH, [0] * board.WIDTH]
