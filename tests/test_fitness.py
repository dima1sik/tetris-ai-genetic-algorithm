import pytest

from ga.fitness import calculate_fitness


def test_fitness_averages_games_and_penalizes_variation(monkeypatch):
    results = {
        1: {"score": 100, "lines": 1, "moves": 10},
        2: {"score": 300, "lines": 3, "moves": 20},
    }
    monkeypatch.setattr("ga.fitness.run_bot_game", lambda seed, **kwargs: results[seed])
    result = calculate_fitness({}, seeds=[1, 2])
    assert result["average_score"] == 200
    assert result["average_lines"] == 2
    assert result["average_moves"] == 15
    assert result["score_std"] == 100
    assert result["lines_std"] == 1
    assert result["stability_penalty"] == 15
    assert result["fitness"] == 315


def test_empty_seed_set_is_rejected():
    with pytest.raises(ValueError, match="seed"):
        calculate_fitness({}, seeds=[])
