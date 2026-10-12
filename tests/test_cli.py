import pytest

from main import main


@pytest.mark.parametrize("arguments", [["demo", "-1"], ["train", "invalid"], ["unknown"]])
def test_cli_rejects_invalid_commands_without_running_games(arguments):
    with pytest.raises(SystemExit) as error:
        main(arguments)
    assert error.value.code == 2


def test_cli_reports_missing_model_cleanly(tmp_path, capsys):
    with pytest.raises(SystemExit) as error:
        main(["eval", "1", "--model", str(tmp_path / "missing.json")])
    assert error.value.code == 2
    assert "missing.json" in capsys.readouterr().err
