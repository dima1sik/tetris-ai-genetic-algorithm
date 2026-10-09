import random

import pytest

from ga.genome import FEATURE_NAMES, Genome
from ga.operators import crossover, mutate, tournament_selection
from ga.population import create_initial_population
from ga.trainer import train_genetic_algorithm


def test_seeded_operators_preserve_parents_and_reset_child_fitness():
    parent_a = Genome({feature: -1 for feature in FEATURE_NAMES})
    parent_b = Genome({feature: 1 for feature in FEATURE_NAMES})
    parent_a.set_fitness(10)
    before_a, before_b = parent_a.weights.copy(), parent_b.weights.copy()
    child = crossover(parent_a, parent_b, random.Random(12))
    assert all(weight in (-1, 1) for weight in child.weights.values())
    assert child.fitness is None
    unmutated = mutate(parent_a, mutation_rate=0, rng=random.Random(12))
    assert unmutated.weights == parent_a.weights
    assert unmutated.fitness is None
    mutated = mutate(child, mutation_rate=1, mutation_strength=0.5, rng=random.Random(12))
    repeated = mutate(child, mutation_rate=1, mutation_strength=0.5, rng=random.Random(12))
    assert mutated.weights == repeated.weights
    assert all(abs(mutated.weights[name] - child.weights[name]) <= 0.5 for name in FEATURE_NAMES)
    assert parent_a.weights == before_a
    assert parent_b.weights == before_b


def test_tournament_selects_best_sampled_genome_even_when_fitness_is_negative():
    population = create_initial_population(5, 12)
    for index, genome in enumerate(population):
        genome.set_fitness(index - 10)
    sampled = random.Random(12).sample(population, 3)
    winner = tournament_selection(population, 3, random.Random(12))
    assert winner is max(sampled, key=lambda genome: genome.fitness)


def test_tournament_requires_valid_size_and_evaluated_genomes():
    population = create_initial_population(2)
    with pytest.raises(ValueError, match="Tournament size"):
        tournament_selection(population, 3)
    with pytest.raises(ValueError, match="evaluated"):
        tournament_selection(population, 2)


def test_training_evaluates_exact_number_of_generations_and_retains_best(monkeypatch):
    evaluated = []

    def evaluate(population, max_moves):
        evaluated.append(population)
        # Deliberately make the final generation worse to check best-ever tracking.
        for index, genome in enumerate(population):
            genome.set_fitness(100 * (3 - len(evaluated)) + index)

    monkeypatch.setattr("ga.trainer.evaluate_population", evaluate)
    result = train_genetic_algorithm(population_size=3, generations=2, max_moves=1, elitism_count=0)
    assert len(evaluated) == 2
    assert [item["generation"] for item in result["history"]] == [1, 2]
    assert result["best_fitness"] == 202
    assert result["best_weights"] == result["history"][0]["best_weights"]


@pytest.mark.parametrize("configuration", [
    {"population_size": 0}, {"generations": 0}, {"max_moves": -1},
    {"elitism_count": 4}, {"tournament_size": 4},
    {"mutation_rate": 1.1}, {"mutation_strength": -1}, {"mutation_strength": float("nan")},
])
def test_invalid_training_config_fails_before_evaluation(monkeypatch, configuration):
    def unexpected_evaluation(*args, **kwargs):
        pytest.fail("An invalid configuration must fail before evaluating games")

    monkeypatch.setattr("ga.trainer.evaluate_population", unexpected_evaluation)
    config = {"population_size": 3, "generations": 1, "max_moves": 1}
    config.update(configuration)
    with pytest.raises(ValueError):
        train_genetic_algorithm(**config)


def test_real_training_is_repeatable_and_elitism_preserves_best_fitness():
    config = {"population_size": 3, "generations": 2, "max_moves": 4, "seed": 12}
    first = train_genetic_algorithm(**config)
    second = train_genetic_algorithm(**config)
    assert first["best_weights"] == second["best_weights"]
    assert first["best_fitness"] == second["best_fitness"]
    assert first["history"] == second["history"]
    assert first["history"][1]["best_fitness"] >= first["history"][0]["best_fitness"]
