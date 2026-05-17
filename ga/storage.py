import json
import os


def save_genome(weights, fitness, path="models/best_genome.json"):
    os.makedirs(os.path.dirname(path), exist_ok=True)

    data = {
        "fitness": fitness,
        "weights": weights,
    }

    with open(path, "w") as file:
        json.dump(data, file, indent=4)

    print(f"Genome saved to: {path}")


def load_genome(path="models/best_genome.json"):
    with open(path, "r") as file:
        data = json.load(file)

    return data