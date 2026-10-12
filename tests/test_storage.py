import json

import pytest

from ai.bot import Bot
from audit.logger import AuditLogger
from ga.storage import load_genome, save_genome


def test_model_and_audit_accept_bare_filenames(monkeypatch, tmp_path):
    monkeypatch.chdir(tmp_path)
    save_genome(Bot.DEFAULT_WEIGHTS, 12.5, "genome.json")
    assert load_genome("genome.json") == {"weights": Bot.DEFAULT_WEIGHTS, "fitness": 12.5}
    logger = AuditLogger("audit.jsonl")
    logger.log_event("test", {"name": "Vilnius / Вильнюс"})
    entry = json.loads((tmp_path / "audit.jsonl").read_text(encoding="utf-8"))
    assert entry["data"]["name"] == "Vilnius / Вильнюс"
    assert entry["timestamp"].endswith("+00:00")


@pytest.mark.parametrize("data", [{}, {"weights": {}, "fitness": 1}, {"weights": Bot.DEFAULT_WEIGHTS, "fitness": float("nan")}])
def test_invalid_saved_genome_is_rejected(tmp_path, data):
    path = tmp_path / "genome.json"
    path.write_text(json.dumps(data), encoding="utf-8")
    with pytest.raises(ValueError):
        load_genome(path)


def test_failed_save_preserves_existing_genome(monkeypatch, tmp_path):
    path = tmp_path / "genome.json"
    save_genome(Bot.DEFAULT_WEIGHTS, 1, path)
    before = path.read_bytes()

    def broken_dump(*args, **kwargs):
        raise OSError("Disk write failed")

    monkeypatch.setattr("ga.storage.json.dump", broken_dump)
    with pytest.raises(OSError):
        save_genome(Bot.DEFAULT_WEIGHTS, 2, path)
    assert path.read_bytes() == before
    assert not path.with_suffix(".json.tmp").exists()
