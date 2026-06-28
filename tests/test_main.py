from unittest.mock import MagicMock, patch

import pytest

from wohnung_agent.main import build_runner, main
from wohnung_agent.models import AppConfig, DemoAdapterConfig, ImmoweltAdapterConfig, TelegramConfig, EmailConfig


def base_config() -> AppConfig:
    return AppConfig(
        max_warm_rent=800,
        min_rooms=2.5,
        kitchen_required=True,
        regions=["Boizenburg"],
        language="en",
        database_path="wohnungen.sqlite3",
        demo=DemoAdapterConfig(enabled=True),
        immowelt=ImmoweltAdapterConfig(enabled=False),
        telegram=TelegramConfig(enabled=False),
        email=EmailConfig(enabled=False),
    )


def test_build_runner_returns_runner_with_demo_adapter():
    with patch("wohnung_agent.main.load_config", return_value=base_config()):
        runner = build_runner("config/search_profile.yml")
    assert runner.adapters


def test_build_runner_raises_when_no_adapters_enabled():
    config = base_config()
    config.demo.enabled = False
    config.immowelt.enabled = False
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


def _database_context(database_mock: MagicMock) -> MagicMock:
    database_context = MagicMock()
    database_context.__enter__.return_value = database_mock
    database_context.__exit__.return_value = None
    return database_context


def test_main_report_open_uses_management_mode_without_runner():
    database_mock = MagicMock()
    database_mock.get_open_apartments.return_value = []

    with patch("wohnung_agent.main.build_runner") as build_runner_mock:
        with patch("wohnung_agent.main.load_config", return_value=base_config()):
            with patch("wohnung_agent.main.ApartmentDatabase", return_value=_database_context(database_mock)):
                with patch("wohnung_agent.main.generate_open_apartments_markdown", return_value="# report"):
                    with patch("builtins.print") as print_mock:
                        with patch("sys.argv", ["wohnung-agent", "--report-open"]):
                            main()

    build_runner_mock.assert_not_called()
    database_mock.get_open_apartments.assert_called_once_with(7)
    print_mock.assert_called()


def test_main_delete_key_calls_database_delete():
    database_mock = MagicMock()
    database_mock.delete_apartment.return_value = True

    with patch("wohnung_agent.main.load_config", return_value=base_config()):
        with patch("wohnung_agent.main.ApartmentDatabase", return_value=_database_context(database_mock)):
            with patch("builtins.print"):
                with patch("sys.argv", ["wohnung-agent", "--delete-key", "immowelt:123"]):
                    main()

    database_mock.delete_apartment.assert_called_once_with("immowelt:123")


def test_main_delete_older_than_days_calls_database_cleanup():
    database_mock = MagicMock()
    database_mock.delete_apartments_older_than_days.return_value = 2

    with patch("wohnung_agent.main.load_config", return_value=base_config()):
        with patch("wohnung_agent.main.ApartmentDatabase", return_value=_database_context(database_mock)):
            with patch("builtins.print"):
                with patch("sys.argv", ["wohnung-agent", "--delete-older-than-days", "7"]):
                    main()

    database_mock.delete_apartments_older_than_days.assert_called_once_with(7)


def test_main_report_output_writes_file(tmp_path):
    output_path = tmp_path / "report.md"
    database_mock = MagicMock()
    database_mock.get_open_apartments.return_value = []

    with patch("wohnung_agent.main.load_config", return_value=base_config()):
        with patch("wohnung_agent.main.ApartmentDatabase", return_value=_database_context(database_mock)):
            with patch("wohnung_agent.main.generate_open_apartments_markdown", return_value="# markdown report"):
                with patch("builtins.print"):
                    with patch(
                        "sys.argv",
                        [
                            "wohnung-agent",
                            "--report-open",
                            "--report-output",
                            str(output_path),
                        ],
                    ):
                        main()

    assert output_path.read_text(encoding="utf-8") == "# markdown report"