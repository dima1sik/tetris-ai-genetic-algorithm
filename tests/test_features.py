from ai.features import extract_features


def test_empty_board_features():
    board = [[0 for _ in range(10)] for _ in range(20)]

    features = extract_features(board)

    assert features["holes"] == 0
    assert features["aggregate_height"] == 0
    assert features["max_height"] == 0
    assert features["bumpiness"] == 0


def test_board_with_single_block_height():
    board = [[0 for _ in range(10)] for _ in range(20)]
    board[19][0] = 1

    features = extract_features(board)

    assert features["aggregate_height"] == 1
    assert features["max_height"] == 1


def test_hole_detection():
    board = [[0 for _ in range(10)] for _ in range(20)]
    board[18][0] = 1
    board[19][0] = 0

    features = extract_features(board)

    assert features["holes"] == 1