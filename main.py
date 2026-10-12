import argparse

from ai.bot import Bot
from audit.logger import AuditLogger, DEFAULT_AUDIT_PATH
from ga.evaluation import evaluate_weights_on_seed_sets
from ga.storage import DEFAULT_MODEL_PATH, load_genome, save_genome
from ga.trainer import train_genetic_algorithm
from simulation.runner import run_bot_game


DEFAULT_TRAIN_MOVES = 100
DEFAULT_DEMO_MOVES = 500
DEFAULT_EVAL_MOVES = 500


def positive_int(value):
    try:
        number = int(value)
    except ValueError as error:
        raise argparse.ArgumentTypeError("must be a positive integer") from error
    if number <= 0:
        raise argparse.ArgumentTypeError("must be a positive integer")
    return number


def print_evaluation_result(name, result):
    print(f"\n{name.upper()}")
    for label, key in (
        ("Fitness", "fitness"),
        ("Average score", "average_score"),
        ("Average lines", "average_lines"),
        ("Average moves", "average_moves"),
        ("Score std", "score_std"),
        ("Lines std", "lines_std"),
        ("Stability penalty", "stability_penalty"),
    ):
        print(f"{label}:", result[key])
    print("Games:", len(result["games"]))


def run_demo(max_moves=DEFAULT_DEMO_MOVES, seed=42, model_path=DEFAULT_MODEL_PATH, audit_path=DEFAULT_AUDIT_PATH):
    try:
        genome = load_genome(model_path)
        weights = genome["weights"]
        print(f"Using trained genome from {model_path}")
        print("Genome fitness:", genome["fitness"])
    except FileNotFoundError:
        weights = Bot.DEFAULT_WEIGHTS
        print("No trained genome found. Using default heuristic weights.")

    result = run_bot_game(
        seed=seed,
        weights=weights,
        max_moves=max_moves,
        audit_logger=AuditLogger(audit_path),
    )
    print("\nDEMO RESULT")
    print("Max moves:", max_moves)
    for label, key in (("Score", "score"), ("Lines", "lines"), ("Moves", "moves"), ("Game over", "game_over")):
        print(f"{label}:", result[key])
    print(f"Audit saved to {audit_path}")
    return result


def run_training(max_moves=DEFAULT_TRAIN_MOVES, model_path=DEFAULT_MODEL_PATH, audit_path=DEFAULT_AUDIT_PATH, **config):
    result = train_genetic_algorithm(
        max_moves=max_moves,
        audit_logger=AuditLogger(audit_path),
        **config,
    )
    save_genome(result["best_weights"], result["best_fitness"], model_path)
    print("\nTRAINING FINISHED")
    print("Max moves:", max_moves)
    print("Best fitness:", result["best_fitness"])
    return result


def run_evaluation(max_moves=DEFAULT_EVAL_MOVES, model_path=DEFAULT_MODEL_PATH):
    genome = load_genome(model_path)
    evaluation = evaluate_weights_on_seed_sets(genome["weights"], max_moves=max_moves)
    print("LOADED GENOME FITNESS:", genome["fitness"])
    print("Evaluation max moves:", max_moves)
    for name, result in evaluation.items():
        print_evaluation_result(name, result)
    return evaluation


def create_parser():
    parser = argparse.ArgumentParser(description="Train and evaluate a deterministic Tetris heuristic bot.")
    commands = parser.add_subparsers(dest="mode")
    for mode, description, default_moves in (
        ("demo", "Run one bot game", DEFAULT_DEMO_MOVES),
        ("train", "Train the genetic algorithm and save the best genome", DEFAULT_TRAIN_MOVES),
        ("eval", "Evaluate a saved genome on train, validation and test seeds", DEFAULT_EVAL_MOVES),
    ):
        command = commands.add_parser(mode, help=description)
        command.add_argument("max_moves", nargs="?", type=positive_int, default=default_moves)
        command.add_argument("--model", default=DEFAULT_MODEL_PATH, help="Genome JSON path")
        if mode != "eval":
            command.add_argument("--audit", default=DEFAULT_AUDIT_PATH, help="Decision/training log path")
            command.add_argument("--seed", type=int, default=123 if mode == "train" else 42)
        if mode == "train":
            command.add_argument("--population-size", type=positive_int, default=30)
            command.add_argument("--generations", type=positive_int, default=20)
            command.add_argument("--elitism-count", type=int, default=1)
            command.add_argument("--tournament-size", type=positive_int, default=3)
            command.add_argument("--mutation-rate", type=float, default=0.2)
            command.add_argument("--mutation-strength", type=float, default=1.0)
    commands.add_parser("help", help="Show command help")
    return parser


def main(argv=None):
    parser = create_parser()
    args = parser.parse_args(argv)
    if args.mode in (None, "help"):
        parser.print_help()
        return
    try:
        if args.mode == "demo":
            run_demo(args.max_moves, args.seed, args.model, args.audit)
        elif args.mode == "train":
            run_training(
                args.max_moves,
                args.model,
                args.audit,
                seed=args.seed,
                population_size=args.population_size,
                generations=args.generations,
                elitism_count=args.elitism_count,
                tournament_size=args.tournament_size,
                mutation_rate=args.mutation_rate,
                mutation_strength=args.mutation_strength,
            )
        else:
            run_evaluation(args.max_moves, args.model)
    except (OSError, ValueError) as error:
        parser.error(str(error))


if __name__ == "__main__":
    main()
