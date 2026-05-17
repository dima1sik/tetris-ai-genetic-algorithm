import statistics

from simulation.runner import run_bot_game
from data.seeds import TRAIN_SEEDS


def calculate_fitness(weights, seeds=None, max_moves=500):
    if seeds is None:
        seeds = TRAIN_SEEDS

    results = []

    for seed in seeds:
        result = run_bot_game(
            seed=seed,
            weights=weights,
            max_moves=max_moves
        )
        results.append(result)

    total_score = sum(result["score"] for result in results)
    total_lines = sum(result["lines"] for result in results)
    total_moves = sum(result["moves"] for result in results)

    average_score = total_score / len(results)
    average_lines = total_lines / len(results)
    average_moves = total_moves / len(results)

    scores = [result["score"] for result in results]
    lines = [result["lines"] for result in results]

    score_std = statistics.pstdev(scores) if len(scores) > 1 else 0
    lines_std = statistics.pstdev(lines) if len(lines) > 1 else 0

    stability_penalty = (
        score_std * 0.10
        + lines_std * 5
    )

    fitness = (
        average_score
        + average_lines * 50
        + average_moves * 2
        - stability_penalty
    )

    return {
        "fitness": fitness,
        "average_score": average_score,
        "average_lines": average_lines,
        "average_moves": average_moves,
        "score_std": score_std,
        "lines_std": lines_std,
        "stability_penalty": stability_penalty,
        "games": results,
    }