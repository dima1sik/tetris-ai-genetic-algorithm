import sys

from ai.bot import Bot
from simulation.runner import run_bot_game
from ga.trainer import train_genetic_algorithm
from ga.evaluation import evaluate_weights_on_seed_sets
from ga.storage import save_genome, load_genome
from audit.logger import AuditLogger


DEFAULT_TRAIN_MOVES = 100
DEFAULT_DEMO_MOVES = 500
DEFAULT_EVAL_MOVES = 500


def get_int_arg(index, default_value):
    if len(sys.argv) <= index:
        return default_value

    try:
        return int(sys.argv[index])
    except ValueError:
        print(f"Invalid number: {sys.argv[index]}")
        print(f"Using default value: {default_value}")
        return default_value


def print_evaluation_result(name, result):
    print(f"\n{name.upper()}")
    print("Fitness:", result["fitness"])
    print("Average score:", result["average_score"])
    print("Average lines:", result["average_lines"])
    print("Average moves:", result["average_moves"])

    if "score_std" in result:
        print("Score std:", result["score_std"])

    if "lines_std" in result:
        print("Lines std:", result["lines_std"])

    if "stability_penalty" in result:
        print("Stability penalty:", result["stability_penalty"])

    print("Games:", len(result["games"]))


def run_demo(max_moves=DEFAULT_DEMO_MOVES):
    try:
        genome = load_genome()
        weights = genome["weights"]
        print("Using trained genome from models/best_genome.json")
        print("Genome fitness:", genome["fitness"])
    except FileNotFoundError:
        weights = Bot.DEFAULT_WEIGHTS
        print("No trained genome found. Using default heuristic weights.")

    logger = AuditLogger()

    result = run_bot_game(
        seed=42,
        weights=weights,
        max_moves=max_moves,
        audit_logger=logger
    )

    print("\nDEMO RESULT")
    print("Max moves:", max_moves)
    print("Score:", result["score"])
    print("Lines:", result["lines"])
    print("Moves:", result["moves"])
    print("Game over:", result["game_over"])
    print("Last move:", result["last_move"])
    print("Last features:", result["last_features"])
    print("Last reasons:", result["last_reasons"])
    print("Audit saved to audit/audit_log.jsonl")


def run_training(max_moves=DEFAULT_TRAIN_MOVES):
    logger = AuditLogger()

    result = train_genetic_algorithm(
        population_size=30,
        generations=20,
        seed=123,
        max_moves=max_moves,
        elitism_count=1,
        tournament_size=3,
        mutation_rate=0.2,
        mutation_strength=1.0,
        audit_logger=logger,
    )

    save_genome(
        weights=result["best_weights"],
        fitness=result["best_fitness"],
    )

    print("\nTRAINING FINISHED")
    print("Max moves:", max_moves)
    print("Best fitness:", result["best_fitness"])
    print("Best weights:", result["best_weights"])


def run_evaluation(max_moves=DEFAULT_EVAL_MOVES):
    genome = load_genome()
    weights = genome["weights"]

    evaluation = evaluate_weights_on_seed_sets(
        weights=weights,
        max_moves=max_moves,
    )

    print("LOADED GENOME FITNESS:", genome["fitness"])
    print("Evaluation max moves:", max_moves)

    print_evaluation_result("train", evaluation["train"])
    print_evaluation_result("validation", evaluation["validation"])
    print_evaluation_result("test", evaluation["test"])


def print_help():
    print("Usage:")
    print("  python main.py demo [max_moves]   - run bot demo")
    print("  python main.py train [max_moves]  - train GA and save best genome")
    print("  python main.py eval [max_moves]   - evaluate saved best genome")
    print("  python main.py help               - show this help")
    print()
    print("Defaults:")
    print(f"  train max_moves = {DEFAULT_TRAIN_MOVES}")
    print(f"  demo max_moves  = {DEFAULT_DEMO_MOVES}")
    print(f"  eval max_moves  = {DEFAULT_EVAL_MOVES}")


def main():
    mode = sys.argv[1] if len(sys.argv) > 1 else "help"

    if mode == "demo":
        max_moves = get_int_arg(2, DEFAULT_DEMO_MOVES)
        run_demo(max_moves)

    elif mode == "train":
        max_moves = get_int_arg(2, DEFAULT_TRAIN_MOVES)
        run_training(max_moves)

    elif mode == "eval":
        max_moves = get_int_arg(2, DEFAULT_EVAL_MOVES)
        run_evaluation(max_moves)

    elif mode == "help":
        print_help()

    else:
        print(f"Unknown mode: {mode}")
        print_help()


if __name__ == "__main__":
    main()