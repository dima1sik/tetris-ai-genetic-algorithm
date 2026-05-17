import random

from ga.genome import Genome, FEATURE_NAMES


def tournament_selection(population, tournament_size=3, rng=None):
    if rng is None:
        rng = random.Random()

    tournament = rng.sample(population, tournament_size)

    return max(
        tournament,
        key=lambda genome: genome.get_fitness()
    )


def crossover(parent_a, parent_b, rng=None):
    if rng is None:
        rng = random.Random()

    child_weights = {}

    for feature in FEATURE_NAMES:
        if rng.random() < 0.5:
            child_weights[feature] = parent_a.get_weights()[feature]
        else:
            child_weights[feature] = parent_b.get_weights()[feature]

    return Genome(child_weights)


def mutate(
    genome,
    mutation_rate=0.2,
    mutation_strength=1.0,
    rng=None
):
    if rng is None:
        rng = random.Random()

    new_weights = genome.get_weights().copy()

    for feature in FEATURE_NAMES:
        if rng.random() < mutation_rate:
            delta = rng.uniform(
                -mutation_strength,
                mutation_strength
            )

            new_weights[feature] += delta

    return Genome(new_weights)