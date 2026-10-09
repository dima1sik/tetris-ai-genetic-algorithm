import math
import random

from ga.genome import Genome, FEATURE_NAMES


def tournament_selection(population, tournament_size=3, rng=None):
    if not 1 <= tournament_size <= len(population):
        raise ValueError("Tournament size must be between 1 and the population size")
    if any(genome.get_fitness() is None for genome in population):
        raise ValueError("Tournament selection requires evaluated genomes")
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
    if not 0 <= mutation_rate <= 1:
        raise ValueError("Mutation rate must be between 0 and 1")
    if not math.isfinite(mutation_strength) or mutation_strength < 0:
        raise ValueError("Mutation strength must be finite and non-negative")

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
