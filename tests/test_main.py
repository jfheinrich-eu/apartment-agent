from unittest.mock import MagicMock, patch

import pytest

from wohnung_agent.main import build_runner, main


def base_config() -> dict:
    return {
        "max_warm_rent": 800,
        "min_rooms": 2.5,
        "kitchen_required": True,
        "regions": ["Boizenburg"],
        "language": "en",
        "database_path": "wohnungen.sqlite3",
        "demo": {"enabled": True},
        "immowelt": {"enabled": False},
        "telegram": {"enabled": False},
        "email": {"enabled": False},
    }


def test_build_runner_returns_runner_with_demo_adapter():
    with patch("wohnung_agent.main.load_config", return_value=base_config()):
        runner = build_runner("config/search_profile.yml")
    assert runner.adapters


def test_build_runner_raises_when_no_adapters_enabled():
    config = base_config()
    config["demo"]["enabled"] = False
    config["immowelt"]["enabled"] = False
    with patch("wohnung_agent.main.load_config", return_value=config):
        with pytest.raises(ValueError):
            build_runner("config/search_profile.yml")


def test_main_runs_once_mode_calls_run_once():
    fake_runner = MagicMock()
    with patch("wohnung_agent.main.build_runner", return_value=fake_runner):
        with patch("sys.argv", ["wohnung-agent", "--once"]):
            main()
    fake_runner.run_once.assert_called_once()


def test_main_scheduler_mode_starts_scheduler():
    fake_runner = MagicMock()
    scheduler_instance = MagicMock()

    with patch("wohnung_agent.main.build_runner", return_value=fake_runner):
        with patch("wohnung_agent.main.BlockingScheduler", return_value=scheduler_instance):
            with patch("sys.argv", ["wohnung-agent"]):
                main()

    scheduler_instance.add_job.assert_called_once()
    scheduler_instance.start.assert_called_once()