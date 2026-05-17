from ga.fitness import calculate_fitness
from data.seeds import TRAIN_SEEDS, VALIDATION_SEEDS, TEST_SEEDS


def evaluate_weights_on_seed_sets(weights, max_moves=500):
    train_result = calculate_fitness(
        weights=weights,
        seeds=TRAIN_SEEDS,
        max_moves=max_moves
    )

    validation_result = calculate_fitness(
        weights=weights,
        seeds=VALIDATION_SEEDS,
        max_moves=max_moves
    )

    test_result = calculate_fitness(
        weights=weights,
        seeds=TEST_SEEDS,
        max_moves=max_moves
    )

    return {
        "train": train_result,
        "validation": validation_result,
        "test": test_result,
    }