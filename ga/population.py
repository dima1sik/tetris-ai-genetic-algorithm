import random

from ga.genome import Genome
from ga.fitness import calculate_fitness
from ga.operators import crossover, mutate, tournament_selection


def create_initial_population(size=30, seed=123):
    if not isinstance(size, int) or size <= 0:
        raise ValueError("Population size must be a positive integer")
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
    if not population or any(genome.get_fitness() is None for genome in population):
        raise ValueError("A non-empty evaluated population is required")

    return max(
        population,
        key=lambda genome: genome.get_fitness()
    )


def evolve_population(
    population,
    elitism_count=1,
    tournament_size=3,
    mutation_rate=0.2,
    mutation_strength=1.0,
    rng=None,
):
    """Breed one generation without modifying the evaluated parent genomes."""
    get_best_genome(population)
    if not isinstance(elitism_count, int) or not 0 <= elitism_count <= len(population):
        raise ValueError("elitism_count must be between 0 and the population size")
    rng = rng if rng is not None else random.Random()
    ranked = sorted(population, key=lambda genome: genome.get_fitness(), reverse=True)
    offspring = [genome.copy() for genome in ranked[:elitism_count]]
    while len(offspring) < len(population):
        parent_a = tournament_selection(population, tournament_size, rng)
        parent_b = tournament_selection(population, tournament_size, rng)
        child = crossover(parent_a, parent_b, rng)
        offspring.append(mutate(child, mutation_rate, mutation_strength, rng))
    return offspring
