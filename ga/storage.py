import json
import math
from numbers import Real
from pathlib import Path

from ai.bot import Bot


DEFAULT_MODEL_PATH = Path(__file__).resolve().parents[1] / "models" / "best_genome.json"


def validate_genome(data):
    if not isinstance(data, dict) or "weights" not in data or "fitness" not in data:
        raise ValueError("Genome must contain weights and fitness")
    if not isinstance(data["weights"], dict) or set(data["weights"]) != set(Bot.DEFAULT_WEIGHTS):
        raise ValueError("Genome must contain all eight feature weights")
    Bot.validate_weights(data["weights"])
    fitness = data["fitness"]
    if isinstance(fitness, bool) or not isinstance(fitness, Real) or not math.isfinite(fitness):
        raise ValueError("Genome fitness must be a finite number")
    return data


def save_genome(weights, fitness, path=DEFAULT_MODEL_PATH):
    path = Path(path)

    data = {
        "fitness": fitness,
        "weights": weights,
    }

    validate_genome(data)
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary_path = path.with_suffix(path.suffix + ".tmp")
    try:
        with temporary_path.open("w", encoding="utf-8") as file:
            json.dump(data, file, indent=4, allow_nan=False)
            file.write("\n")
        temporary_path.replace(path)
    finally:
        temporary_path.unlink(missing_ok=True)

    print(f"Genome saved to: {path}")


def load_genome(path=DEFAULT_MODEL_PATH):
    with Path(path).open("r", encoding="utf-8") as file:
        data = json.load(file)

    return validate_genome(data)
