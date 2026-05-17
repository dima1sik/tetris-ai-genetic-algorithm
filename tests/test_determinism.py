from ai.bot import Bot
from simulation.runner import run_bot_game


def test_same_seed_and_weights_give_same_result():
    result_1 = run_bot_game(
        seed=42,
        weights=Bot.DEFAULT_WEIGHTS,
        max_moves=50
    )

    result_2 = run_bot_game(
        seed=42,
        weights=Bot.DEFAULT_WEIGHTS,
        max_moves=50
    )

    assert result_1["score"] == result_2["score"]
    assert result_1["lines"] == result_2["lines"]
    assert result_1["moves"] == result_2["moves"]
    assert result_1["last_move"] == result_2["last_move"]