import json
from datetime import datetime, timezone
from pathlib import Path


DEFAULT_AUDIT_PATH = Path(__file__).resolve().parents[1] / "audit" / "audit_log.jsonl"


class AuditLogger:
    def __init__(self, path=DEFAULT_AUDIT_PATH):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)

    def log_event(self, event_type, data):
        entry = {
            "timestamp": datetime.now(timezone.utc).isoformat(timespec="seconds"),
            "event_type": event_type,
            "data": data,
        }

        with open(self.path, "a", encoding="utf-8") as file:
            file.write(json.dumps(entry, ensure_ascii=False) + "\n")

    def log_training_start(self, config):
        self.log_event("training_start", {
            "config": config,
        })

    def log_generation_best(self, generation, best_fitness, best_weights):
        self.log_event("generation_best", {
            "generation": generation,
            "best_fitness": best_fitness,
            "best_weights": best_weights,
        })

    def log_game_result(self, result):
        self.log_event("game_result", result)

    def log_decision(self, move, score, features, reasons):
        self.log_event("decision", {
            "move": move,
            "score": score,
            "features": features,
            "reasons": reasons,
        })
