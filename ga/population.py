import random

from ga.genome import Genome
from ga.fitness import calculate_fitness


def create_initial_population(size=30, seed=123):
    rng = random.Random(seed)
    population = []

    for _ in range(size):
        genome = Genome.random_genome(rng)
        population.append(genome)

    return population


def evaluate_population(population, max_moves=200):
    for index, genome in enumerate(population):
        result = calculate_fitness(
            weights=genome.get_weights(),
            max_moves=max_moves
        )

        genome.set_fitness(result["fitness"])

        print(
            f"Genome {index}: "
            f"fitness={result['fitness']:.2f}, "
            f"avg_lines={result['average_lines']:.2f}, "
            f"avg_moves={result['average_moves']:.2f}"
        )

    return population


def get_best_genome(population):
    return max(
        population,
        key=lambda genome: genome.get_fitness()
    )