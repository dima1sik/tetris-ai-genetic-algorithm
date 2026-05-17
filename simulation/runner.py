from core.game import Game
from ai.bot import Bot


def run_bot_game(seed=42, weights=None, max_moves=500, audit_logger=None):
    game = Game(seed=seed)
    bot = Bot(weights=weights)

    moves_played = 0

    while not game.is_game_over() and moves_played < max_moves:
        move = bot.find_best_move(
            game.board,
            game.get_current_piece()
        )

        if move is None:
            break

        if audit_logger is not None:
            audit_logger.log_decision(
                move=bot.get_last_move(),
                score=bot.get_last_score(),
                features=bot.get_features(),
                reasons=bot.get_last_reasons(),
            )

        game.apply_bot_move(move)
        moves_played += 1

    result = {
        "seed": seed,
        "score": game.get_score(),
        "lines": game.get_lines(),
        "moves": moves_played,
        "game_over": game.is_game_over(),
        "last_features": bot.get_features(),
        "last_move": bot.get_last_move(),
        "last_score": bot.get_last_score(),
        "last_reasons": bot.get_last_reasons(),
    }

    if audit_logger is not None:
        audit_logger.log_game_result(result)

    return result