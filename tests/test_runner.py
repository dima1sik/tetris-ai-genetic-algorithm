from simulation.runner import run_bot_game


def test_runner_returns_expected_keys():
    result = run_bot_game(seed=42, max_moves=5)

    assert "score" in result
    assert "lines" in result
    assert "moves" in result
    assert "game_over" in result
    assert "last_features" in result
    assert "last_move" in result


def test_runner_respects_max_moves():
    result = run_bot_game(seed=42, max_moves=5)

    assert result["moves"] <= 5