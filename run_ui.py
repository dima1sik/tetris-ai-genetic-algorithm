import random

import pygame

from ai.bot import Bot
from audit.logger import AuditLogger
from core.game import Game
from ga.operators import crossover, mutate, tournament_selection
from ga.population import create_initial_population
from ga.storage import load_genome
from ui.panels import InfoPanel
from ui.renderer import BoardRenderer


WINDOW_WIDTH = 1280
WINDOW_HEIGHT = 760
FPS = 60

DEFAULT_SEED = 42
MAX_MOVES = 500
MAX_RECENT_LOGS = 8

BACKGROUND_COLOR = (14, 17, 23)

SPEED_OPTIONS = {
    "slow": 1000,
    "normal": 400,
    "fast": 100,
}

TRAIN_UI_POPULATION_SIZE = 12
TRAIN_UI_GENERATIONS = 5
TRAIN_UI_MAX_MOVES = 80
TRAIN_UI_SEED = 123
TRAIN_UI_GAME_SEED = 42
TRAIN_UI_MUTATION_RATE = 0.2
TRAIN_UI_MUTATION_STRENGTH = 1.0
TRAIN_UI_TOURNAMENT_SIZE = 3


def load_bot_weights():
    try:
        genome = load_genome()
        return genome["weights"], "trained genome"
    except FileNotFoundError:
        return Bot.DEFAULT_WEIGHTS, "default weights"


def parse_seed(seed_text):
    try:
        return int(seed_text)
    except ValueError:
        return DEFAULT_SEED


def create_game_and_bot(seed, weights):
    game = Game(seed=seed)
    bot = Bot(weights=weights)
    return game, bot


def get_current_piece_name(game):
    current_piece = game.get_current_piece()

    if current_piece is None:
        return "N/A"

    return getattr(current_piece, "name", str(current_piece))


def format_score(value):
    if isinstance(value, float):
        return f"{value:.2f}"

    return str(value)


def add_recent_log(recent_logs, message):
    recent_logs.append(message)

    while len(recent_logs) > MAX_RECENT_LOGS:
        recent_logs.pop(0)


def log_ui_event(logger, event_name, data=None):
    if data is None:
        data = {}

    logger.log_event(
        "ui_event",
        {
            "name": event_name,
            **data,
        },
    )


def log_ui_decision(logger, bot, move, moves_played, seed, speed, mode):
    logger.log_decision(
        move=move,
        score=bot.get_last_score(),
        features=bot.get_features(),
        reasons=bot.get_last_reasons(),
    )

    logger.log_event(
        "ui_decision_context",
        {
            "moves_played": moves_played,
            "seed": seed,
            "speed": speed,
            "mode": mode,
        },
    )


def log_ui_game_result(logger, game, bot, moves_played, max_moves, seed, finish_reason):
    result = {
        "source": "ui",
        "seed": seed,
        "score": game.get_score(),
        "lines": game.get_lines(),
        "moves": moves_played,
        "max_moves": max_moves,
        "game_over": game.is_game_over(),
        "finish_reason": finish_reason,
        "last_features": bot.get_features(),
        "last_move": bot.get_last_move(),
        "last_score": bot.get_last_score(),
        "last_reasons": bot.get_last_reasons(),
    }

    logger.log_game_result(result)


def get_finish_reason(game, moves_played, max_moves, no_available_move):
    if game.is_game_over():
        return "game_over"

    if no_available_move:
        return "no_available_move"

    if moves_played >= max_moves:
        return "max_moves"

    return "running"


def calculate_train_fitness(agent):
    return (
        agent["game"].get_score()
        + agent["game"].get_lines() * 50
        + agent["moves"] * 2
    )


def create_train_agent(index, genome, game_seed):
    return {
        "index": index,
        "genome": genome,
        "game": Game(seed=game_seed),
        "bot": Bot(weights=genome.get_weights()),
        "moves": 0,
        "finished": False,
        "fitness": None,
        "status": "running",
    }


def create_train_agents(population, game_seed):
    agents = []

    for index, genome in enumerate(population):
        agents.append(
            create_train_agent(
                index=index,
                genome=genome,
                game_seed=game_seed,
            )
        )

    return agents


def create_initial_train_state():
    population = create_initial_population(
        size=TRAIN_UI_POPULATION_SIZE,
        seed=TRAIN_UI_SEED,
    )

    agents = create_train_agents(
        population=population,
        game_seed=TRAIN_UI_GAME_SEED,
    )

    return {
        "rng": random.Random(TRAIN_UI_SEED),
        "population": population,
        "agents": agents,
        "generation": 1,
        "max_generations": TRAIN_UI_GENERATIONS,
        "generation_finished": False,
        "best_agent_index": None,
        "best_fitness": None,
        "logs": ["Generation 1 started"],
    }


def finish_train_agent(agent, reason):
    if agent["finished"]:
        return

    agent["finished"] = True
    agent["status"] = reason
    agent["fitness"] = calculate_train_fitness(agent)
    agent["genome"].set_fitness(agent["fitness"])


def get_best_train_agent(train_state):
    agents = train_state["agents"]
    finished_agents = [agent for agent in agents if agent["fitness"] is not None]

    if not finished_agents:
        return None

    return max(finished_agents, key=lambda agent: agent["fitness"])


def evaluate_train_generation(train_state, recent_logs, audit_logger):
    if train_state["generation_finished"]:
        return

    for agent in train_state["agents"]:
        if agent["fitness"] is None:
            finish_train_agent(agent, "finished")

    best_agent = get_best_train_agent(train_state)

    if best_agent is not None:
        train_state["best_agent_index"] = best_agent["index"]
        train_state["best_fitness"] = best_agent["fitness"]

        message = (
            f"Generation {train_state['generation']} finished: "
            f"best G#{best_agent['index']} fitness={best_agent['fitness']}"
        )

        train_state["logs"].append(message)
        add_recent_log(recent_logs, message)

        audit_logger.log_generation_best(
            generation=train_state["generation"],
            best_fitness=best_agent["fitness"],
            best_weights=best_agent["genome"].get_weights(),
        )

    train_state["generation_finished"] = True


def update_train_agents(train_state, recent_logs, audit_logger):
    if train_state["generation_finished"]:
        return

    active_count = 0

    for agent in train_state["agents"]:
        if agent["finished"]:
            continue

        active_count += 1

        game = agent["game"]
        bot = agent["bot"]

        move = bot.find_best_move(
            game.board,
            game.get_current_piece(),
        )

        if move is None:
            finish_train_agent(agent, "no move")
            train_state["logs"].append(
                f"G#{agent['index']} finished: no move, fitness={agent['fitness']}"
            )
            continue

        game.apply_bot_move(move)
        agent["moves"] += 1

        if game.is_game_over():
            finish_train_agent(agent, "game over")
            train_state["logs"].append(
                f"G#{agent['index']} finished: game over, fitness={agent['fitness']}"
            )

        elif agent["moves"] >= TRAIN_UI_MAX_MOVES:
            finish_train_agent(agent, "max moves")
            train_state["logs"].append(
                f"G#{agent['index']} finished: max moves, fitness={agent['fitness']}"
            )

    if active_count == 0 or all(agent["finished"] for agent in train_state["agents"]):
        evaluate_train_generation(
            train_state=train_state,
            recent_logs=recent_logs,
            audit_logger=audit_logger,
        )


def create_next_train_generation(train_state, recent_logs, audit_logger):
    if not train_state["generation_finished"]:
        return train_state

    if train_state["generation"] >= train_state["max_generations"]:
        add_recent_log(recent_logs, "Train mode reached final generation")
        train_state["logs"].append("Final train generation reached")
        return train_state

    old_population = [agent["genome"] for agent in train_state["agents"]]

    for agent in train_state["agents"]:
        agent["genome"].set_fitness(agent["fitness"])

    sorted_population = sorted(
        old_population,
        key=lambda genome: genome.get_fitness(),
        reverse=True,
    )

    rng = train_state["rng"]
    new_population = [sorted_population[0].copy()]

    while len(new_population) < TRAIN_UI_POPULATION_SIZE:
        parent_a = tournament_selection(
            old_population,
            tournament_size=TRAIN_UI_TOURNAMENT_SIZE,
            rng=rng,
        )
        parent_b = tournament_selection(
            old_population,
            tournament_size=TRAIN_UI_TOURNAMENT_SIZE,
            rng=rng,
        )

        child = crossover(parent_a, parent_b, rng=rng)
        child = mutate(
            child,
            mutation_rate=TRAIN_UI_MUTATION_RATE,
            mutation_strength=TRAIN_UI_MUTATION_STRENGTH,
            rng=rng,
        )

        new_population.append(child)

    new_generation = train_state["generation"] + 1
    game_seed = TRAIN_UI_GAME_SEED + new_generation

    new_state = {
        "rng": rng,
        "population": new_population,
        "agents": create_train_agents(new_population, game_seed),
        "generation": new_generation,
        "max_generations": train_state["max_generations"],
        "generation_finished": False,
        "best_agent_index": None,
        "best_fitness": None,
        "logs": train_state["logs"][-8:] + [f"Generation {new_generation} started"],
    }

    add_recent_log(
        recent_logs,
        f"Generation {new_generation} created",
    )

    log_ui_event(
        audit_logger,
        "train_generation_created",
        {
            "generation": new_generation,
            "population_size": TRAIN_UI_POPULATION_SIZE,
            "game_seed": game_seed,
        },
    )

    return new_state


def main():
    pygame.init()

    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    pygame.display.set_caption("TetrisGA Demo")

    clock = pygame.time.Clock()

    audit_logger = AuditLogger()

    weights, weights_label = load_bot_weights()

    selected_seed = DEFAULT_SEED
    seed_text = str(DEFAULT_SEED)
    seed_input_active = False

    selected_speed = "normal"
    move_delay_ms = SPEED_OPTIONS[selected_speed]

    selected_mode = "demo"
    is_playing = True

    game, bot = create_game_and_bot(selected_seed, weights)
    train_state = create_initial_train_state()

    board_renderer = BoardRenderer(x=24, y=34, cell_size=26)
    demo_panel = InfoPanel(x=332, y=34, width=920, height=690)
    train_panel = InfoPanel(x=24, y=34, width=1228, height=690)

    moves_played = 0
    no_available_move = False
    last_placed_piece = "N/A"
    final_result_logged = False

    recent_logs = []
    add_recent_log(recent_logs, f"UI started: seed={selected_seed}, mode={selected_mode}")
    add_recent_log(recent_logs, f"Weights: {weights_label}")
    add_recent_log(recent_logs, "Train generation 1 ready")

    last_demo_step_time = pygame.time.get_ticks()
    last_train_step_time = pygame.time.get_ticks()
    clickable_rects = {}

    log_ui_event(
        audit_logger,
        "ui_started",
        {
            "seed": selected_seed,
            "mode": selected_mode,
            "speed": selected_speed,
            "weights": weights_label,
            "max_moves": MAX_MOVES,
            "train_population": TRAIN_UI_POPULATION_SIZE,
            "train_generations": TRAIN_UI_GENERATIONS,
            "train_max_moves": TRAIN_UI_MAX_MOVES,
        },
    )

    running = True

    while running:
        current_time = pygame.time.get_ticks()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                log_ui_event(
                    audit_logger,
                    "ui_window_closed",
                    {
                        "seed": selected_seed,
                        "mode": selected_mode,
                        "moves_played": moves_played,
                        "score": game.get_score(),
                        "lines": game.get_lines(),
                    },
                )
                running = False

            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mouse_position = pygame.mouse.get_pos()
                seed_input_active = False

                if (
                    clickable_rects.get("seed_input")
                    and clickable_rects["seed_input"].collidepoint(mouse_position)
                ):
                    seed_input_active = True
                    add_recent_log(recent_logs, "Seed input focused")

                elif (
                    clickable_rects.get("toggle_play")
                    and clickable_rects["toggle_play"].collidepoint(mouse_position)
                ):
                    is_playing = not is_playing

                    log_ui_event(
                        audit_logger,
                        "playback_toggled",
                        {
                            "mode": selected_mode,
                            "is_playing": is_playing,
                            "moves_played": moves_played,
                            "score": game.get_score(),
                            "lines": game.get_lines(),
                        },
                    )

                    add_recent_log(
                        recent_logs,
                        "Animation started" if is_playing else "Animation paused",
                    )

                elif (
                    clickable_rects.get("reset")
                    and clickable_rects["reset"].collidepoint(mouse_position)
                ):
                    if selected_mode == "demo":
                        selected_seed = parse_seed(seed_text)
                        game, bot = create_game_and_bot(selected_seed, weights)

                        moves_played = 0
                        no_available_move = False
                        last_placed_piece = "N/A"
                        final_result_logged = False

                        is_playing = True
                        last_demo_step_time = pygame.time.get_ticks()

                        add_recent_log(recent_logs, f"Demo reset: seed={selected_seed}")

                        log_ui_event(
                            audit_logger,
                            "demo_reset",
                            {
                                "seed": selected_seed,
                                "speed": selected_speed,
                                "weights": weights_label,
                                "max_moves": MAX_MOVES,
                            },
                        )
                    else:
                        train_state = create_initial_train_state()
                        is_playing = True
                        last_train_step_time = pygame.time.get_ticks()

                        add_recent_log(recent_logs, "Train mode reset to generation 1")

                        log_ui_event(
                            audit_logger,
                            "train_reset",
                            {
                                "generation": 1,
                                "population_size": TRAIN_UI_POPULATION_SIZE,
                                "max_moves": TRAIN_UI_MAX_MOVES,
                            },
                        )

                elif (
                    clickable_rects.get("mode_demo")
                    and clickable_rects["mode_demo"].collidepoint(mouse_position)
                ):
                    selected_mode = "demo"
                    is_playing = True
                    last_demo_step_time = pygame.time.get_ticks()

                    add_recent_log(recent_logs, "Mode changed: demo")

                    log_ui_event(
                        audit_logger,
                        "mode_changed",
                        {
                            "mode": selected_mode,
                        },
                    )

                elif (
                    clickable_rects.get("mode_train")
                    and clickable_rects["mode_train"].collidepoint(mouse_position)
                ):
                    selected_mode = "train"
                    is_playing = True
                    last_train_step_time = pygame.time.get_ticks()

                    add_recent_log(recent_logs, "Mode changed: train")

                    log_ui_event(
                        audit_logger,
                        "mode_changed",
                        {
                            "mode": selected_mode,
                        },
                    )

                elif (
                    clickable_rects.get("next_generation")
                    and clickable_rects["next_generation"].collidepoint(mouse_position)
                ):
                    if selected_mode == "train":
                        train_state = create_next_train_generation(
                            train_state=train_state,
                            recent_logs=recent_logs,
                            audit_logger=audit_logger,
                        )
                        is_playing = True
                        last_train_step_time = pygame.time.get_ticks()

                elif (
                    clickable_rects.get("speed_slow")
                    and clickable_rects["speed_slow"].collidepoint(mouse_position)
                ):
                    selected_speed = "slow"
                    move_delay_ms = SPEED_OPTIONS[selected_speed]
                    add_recent_log(recent_logs, "Speed changed: slow")

                elif (
                    clickable_rects.get("speed_normal")
                    and clickable_rects["speed_normal"].collidepoint(mouse_position)
                ):
                    selected_speed = "normal"
                    move_delay_ms = SPEED_OPTIONS[selected_speed]
                    add_recent_log(recent_logs, "Speed changed: normal")

                elif (
                    clickable_rects.get("speed_fast")
                    and clickable_rects["speed_fast"].collidepoint(mouse_position)
                ):
                    selected_speed = "fast"
                    move_delay_ms = SPEED_OPTIONS[selected_speed]
                    add_recent_log(recent_logs, "Speed changed: fast")

            if event.type == pygame.KEYDOWN and seed_input_active:
                if event.key == pygame.K_BACKSPACE:
                    seed_text = seed_text[:-1]

                elif event.key == pygame.K_RETURN:
                    selected_seed = parse_seed(seed_text)
                    game, bot = create_game_and_bot(selected_seed, weights)

                    moves_played = 0
                    no_available_move = False
                    last_placed_piece = "N/A"
                    final_result_logged = False

                    is_playing = True
                    seed_input_active = False
                    last_demo_step_time = pygame.time.get_ticks()

                    add_recent_log(recent_logs, f"Seed applied: {selected_seed}")

                    log_ui_event(
                        audit_logger,
                        "seed_applied",
                        {
                            "seed": selected_seed,
                            "mode": selected_mode,
                            "speed": selected_speed,
                        },
                    )

                elif event.unicode.isdigit() and len(seed_text) < 9:
                    seed_text += event.unicode

        demo_finished = (
            game.is_game_over()
            or moves_played >= MAX_MOVES
            or no_available_move
        )

        should_run_demo_step = (
            selected_mode == "demo"
            and is_playing
            and not demo_finished
            and current_time - last_demo_step_time >= move_delay_ms
        )

        if should_run_demo_step:
            current_piece_name = get_current_piece_name(game)

            move = bot.find_best_move(
                game.board,
                game.get_current_piece(),
            )

            if move is None:
                no_available_move = True
                add_recent_log(recent_logs, f"No available move after {moves_played} moves")
            else:
                last_move = bot.get_last_move()
                decision_score = bot.get_last_score()

                log_ui_decision(
                    logger=audit_logger,
                    bot=bot,
                    move=last_move,
                    moves_played=moves_played + 1,
                    seed=selected_seed,
                    speed=selected_speed,
                    mode=selected_mode,
                )

                last_placed_piece = current_piece_name
                game.apply_bot_move(move)
                moves_played += 1

                move_piece = last_move.get("piece", "N/A")
                move_rotation = last_move.get("rotation_index", "N/A")
                move_x = last_move.get("x", "N/A")

                add_recent_log(
                    recent_logs,
                    (
                        f"Move {moves_played}: "
                        f"{move_piece} rot={move_rotation} "
                        f"x={move_x} score={format_score(decision_score)}"
                    ),
                )

            last_demo_step_time = current_time

        should_run_train_step = (
            selected_mode == "train"
            and is_playing
            and not train_state["generation_finished"]
            and current_time - last_train_step_time >= move_delay_ms
        )

        if should_run_train_step:
            update_train_agents(
                train_state=train_state,
                recent_logs=recent_logs,
                audit_logger=audit_logger,
            )
            last_train_step_time = current_time

        demo_finished = (
            game.is_game_over()
            or moves_played >= MAX_MOVES
            or no_available_move
        )

        if demo_finished and not final_result_logged:
            finish_reason = get_finish_reason(
                game=game,
                moves_played=moves_played,
                max_moves=MAX_MOVES,
                no_available_move=no_available_move,
            )

            log_ui_game_result(
                logger=audit_logger,
                game=game,
                bot=bot,
                moves_played=moves_played,
                max_moves=MAX_MOVES,
                seed=selected_seed,
                finish_reason=finish_reason,
            )

            add_recent_log(
                recent_logs,
                (
                    f"Demo finished: {finish_reason}, "
                    f"score={game.get_score()}, lines={game.get_lines()}"
                ),
            )

            final_result_logged = True

        screen.fill(BACKGROUND_COLOR)

        ui_state = {
            "selected_mode": selected_mode,
            "is_playing": is_playing,
            "weights_label": weights_label,
            "seed_text": seed_text,
            "seed_input_active": seed_input_active,
            "selected_speed": selected_speed,
            "move_delay_ms": move_delay_ms,
            "moves_played": moves_played,
            "max_moves": MAX_MOVES,
            "demo_finished": demo_finished,
            "no_available_move": no_available_move,
            "current_piece": get_current_piece_name(game),
            "last_placed_piece": last_placed_piece,
            "recent_logs": recent_logs,
            "train_state": train_state,
            "train_population_size": TRAIN_UI_POPULATION_SIZE,
            "train_max_moves": TRAIN_UI_MAX_MOVES,
        }

        if selected_mode == "demo":
            board_renderer.draw(screen, game.get_board())
            clickable_rects = demo_panel.draw(
                surface=screen,
                game=game,
                bot=bot,
                ui_state=ui_state,
            )
        else:
            clickable_rects = train_panel.draw(
                surface=screen,
                game=game,
                bot=bot,
                ui_state=ui_state,
            )

        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()


if __name__ == "__main__":
    main()