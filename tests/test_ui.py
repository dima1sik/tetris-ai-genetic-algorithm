import os

# The dashboard can be exercised without a desktop or audio device in CI.
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame
import pytest

import run_ui
from audit.logger import AuditLogger


def test_visual_generations_keep_same_benchmark_seed(tmp_path):
    state = run_ui.create_initial_train_state()
    for agent in state["agents"]:
        run_ui.finish_train_agent(agent, "test completed")
    logger = AuditLogger(tmp_path / "audit.jsonl")
    run_ui.evaluate_train_generation(state, [], logger)
    next_state = run_ui.create_next_train_generation(state, [], logger)
    assert next_state["generation"] == 2
    assert all(agent["game"].seed == run_ui.TRAIN_UI_GAME_SEED for agent in next_state["agents"])
    assert next_state["population"][0].weights == state["agents"][0]["genome"].weights


def test_corrupt_model_falls_back_to_default_weights(monkeypatch):
    def corrupt_model():
        raise ValueError("Corrupt model")

    monkeypatch.setattr(run_ui, "load_genome", corrupt_model)
    assert run_ui.load_bot_weights() == (run_ui.Bot.DEFAULT_WEIGHTS, "default weights")


def test_full_dashboard_starts_draws_demo_and_training_then_quits(monkeypatch, tmp_path):
    monkeypatch.setattr(run_ui, "AuditLogger", lambda: AuditLogger(tmp_path / "ui.jsonl"))
    monkeypatch.setattr(run_ui, "load_bot_weights", lambda: (run_ui.Bot.DEFAULT_WEIGHTS, "default weights"))
    original_draw = run_ui.InfoPanel.draw
    frames = []
    controls = {}

    def draw(panel, surface, game, bot, ui_state):
        frames.append(ui_state["selected_mode"])
        controls.update(original_draw(panel, surface, game, bot, ui_state))
        return controls

    def events():
        if not frames:
            return []
        if frames[-1] == "demo":
            return [pygame.event.Event(pygame.MOUSEBUTTONDOWN, button=1)]
        return [pygame.event.Event(pygame.QUIT)]

    monkeypatch.setattr(run_ui.InfoPanel, "draw", draw)
    monkeypatch.setattr(pygame.event, "get", events)
    monkeypatch.setattr(pygame.mouse, "get_pos", lambda: controls.get("mode_train", pygame.Rect(0, 0, 1, 1)).center)
    run_ui.main()
    assert "demo" in frames and "train" in frames
    assert not pygame.get_init()


def test_pygame_is_released_when_startup_fails(monkeypatch):
    def fail_startup():
        pygame.init()
        raise RuntimeError("Startup failed")

    monkeypatch.setattr(run_ui, "run_ui", fail_startup)
    with pytest.raises(RuntimeError, match="Startup failed"):
        run_ui.main()
    assert not pygame.get_init()
