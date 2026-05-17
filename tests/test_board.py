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