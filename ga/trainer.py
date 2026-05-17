import random

from ga.population import create_initial_population, evaluate_population, get_best_genome
from ga.operators import tournament_selection, crossover, mutate


def train_genetic_algorithm(
    population_size=30,
    generations=20,
    seed=123,
    max_moves=200,
    elitism_count=1,
    tournament_size=3,
    mutation_rate=0.2,
    mutation_strength=1.0,
    audit_logger=None,
):
    rng = random.Random(seed)

    config = {
        "population_size": population_size,
        "generations": generations,
        "seed": seed,
        "max_moves": max_moves,
        "elitism_count": elitism_count,
        "tournament_size": tournament_size,
        "mutation_rate": mutation_rate,
        "mutation_strength": mutation_strength,
    }

    if audit_logger is not None:
        audit_logger.log_training_start(config)

    population = create_initial_population(
        size=population_size,
        seed=seed
    )

    history = []

    for generation in range(generations):
        print(f"\nGENERATION {generation + 1}/{generations}")

        evaluate_population(
            population,
            max_moves=max_moves
        )

        best_genome = get_best_genome(population)

        history_item = {
            "generation": generation + 1,
            "best_fitness": best_genome.get_fitness(),
            "best_weights": best_genome.get_weights().copy(),
        }

        history.append(history_item)

        if audit_logger is not None:
            audit_logger.log_generation_best(
                generation=generation + 1,
                best_fitness=best_genome.get_fitness(),
                best_weights=best_genome.get_weights().copy(),
            )

        print("Best fitness:", best_genome.get_fitness())

        sorted_population = sorted(
            population,
            key=lambda genome: genome.get_fitness(),
            reverse=True
        )

        new_population = []

        for i in range(elitism_count):
            new_population.append(sorted_population[i].copy())

        while len(new_population) < population_size:
            parent_a = tournament_selection(
                population,
                tournament_size=tournament_size,
                rng=rng
            )

            parent_b = tournament_selection(
                population,
                tournament_size=tournament_size,
                rng=rng
            )

            child = crossover(parent_a, parent_b, rng=rng)

            child = mutate(
                child,
                mutation_rate=mutation_rate,
                mutation_strength=mutation_strength,
                rng=rng
            )

            new_population.append(child)

        population = new_population

    print("\nFINAL POPULATION EVALUATION")

    evaluate_population(
        population,
        max_moves=max_moves
    )

    best_genome = get_best_genome(population)

    final_history_item = {
        "generation": "final",
        "best_fitness": best_genome.get_fitness(),
        "best_weights": best_genome.get_weights().copy(),
    }

    history.append(final_history_item)

    if audit_logger is not None:
        audit_logger.log_event("final_population_best", {
            "best_fitness": best_genome.get_fitness(),
            "best_weights": best_genome.get_weights().copy(),
        })

    result = {
        "best_genome": best_genome,
        "best_weights": best_genome.get_weights(),
        "best_fitness": best_genome.get_fitness(),
        "history": history,
        "config": config,
    }

    if audit_logger is not None:
        audit_logger.log_event("training_finished", {
            "final_best_fitness": result["best_fitness"],
            "final_best_weights": result["best_weights"],
            "history_length": len(history),
        })

    return result