from core.piece import Piece


def test_piece_rotation_count():
    piece = Piece("T")

    assert piece.get_rotation_count() == 4


def test_piece_rotation_changes_blocks():
    piece = Piece("T")
    rotated = piece.get_rotated()

    assert piece.get_blocks() != rotated.get_blocks()


def test_o_piece_has_one_rotation():
    piece = Piece("O")

    assert piece.get_rotation_count() == 1