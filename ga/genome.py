import random


FEATURE_NAMES = [
    "holes",
    "aggregate_height",
    "max_height",
    "bumpiness",
    "lines_cleared",
    "well_sums",
    "row_transitions",
    "column_transitions",
]


class Genome:
    def __init__(self, weights=None):
        if weights is None:
            self.weights = {}
        else:
            self.weights = weights

        self.fitness = None

    @staticmethod
    def random_genome(rng=None):
        if rng is None:
            rng = random.Random()

        weights = {}

        for feature in FEATURE_NAMES:
            weights[feature] = rng.uniform(-5.0, 5.0)

        return Genome(weights)

    def copy(self):
        copied = Genome(self.weights.copy())
        copied.fitness = self.fitness
        return copied

    def get_weights(self):
        return self.weights

    def set_fitness(self, fitness):
        self.fitness = fitness

    def get_fitness(self):
        return self.fitness