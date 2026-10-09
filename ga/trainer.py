import math
import random

from ga.population import create_initial_population, evaluate_population, evolve_population, get_best_genome


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
    for name, value in (("population_size", population_size), ("generations", generations), ("max_moves", max_moves)):
        if not isinstance(value, int) or value <= 0:
            raise ValueError(f"{name} must be a positive integer")
    if not isinstance(elitism_count, int) or not 0 <= elitism_count <= population_size:
        raise ValueError("elitism_count must be between 0 and population_size")
    if not isinstance(tournament_size, int) or not 1 <= tournament_size <= population_size:
        raise ValueError("tournament_size must be between 1 and population_size")
    if not 0 <= mutation_rate <= 1:
        raise ValueError("mutation_rate must be between 0 and 1")
    if not math.isfinite(mutation_strength) or mutation_strength < 0:
        raise ValueError("mutation_strength must be finite and non-negative")

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
    best_overall = None

    for generation in range(generations):
        print(f"\nGENERATION {generation + 1}/{generations}")

        evaluate_population(
            population,
            max_moves=max_moves
        )

        best_genome = get_best_genome(population)
        if best_overall is None or best_genome.get_fitness() > best_overall.get_fitness():
            best_overall = best_genome.copy()

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

        if generation == generations - 1:
            break

        population = evolve_population(
            population,
            elitism_count=elitism_count,
            tournament_size=tournament_size,
            mutation_rate=mutation_rate,
            mutation_strength=mutation_strength,
            rng=rng,
        )

    result = {
        "best_genome": best_overall,
        "best_weights": best_overall.get_weights().copy(),
        "best_fitness": best_overall.get_fitness(),
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
