from __future__ import annotations

import argparse
import logging
from apscheduler.schedulers.blocking import BlockingScheduler
from wohnung_agent.adapters.demo_adapter import DemoAdapter
from wohnung_agent.config_loader import load_config, load_database_path, load_language, load_search_profile
from wohnung_agent.database import ApartmentDatabase
from wohnung_agent.filter_engine import FilterEngine
from wohnung_agent.notifier import Notifier
from wohnung_agent.runner import ApartmentSearchRunner

LOGGER = logging.getLogger(__name__)


def build_runner(config_path: str) -> ApartmentSearchRunner:
    """Create a fully configured runner from the YAML configuration."""
    config = load_config(config_path)
    language = load_language(config)
    profile = load_search_profile(config)

    adapters = []

    if config.get("demo", {}).get("enabled", False):
        adapters.append(DemoAdapter())

    immowelt_config = config.get("immowelt", {})
    if immowelt_config.get("enabled", False):
        try:
            from wohnung_agent.adapters.immowelt_adapter import ImmoweltAdapter
            adapters.append(
                ImmoweltAdapter(
                    search_urls=immowelt_config.get("search_urls", []),
                    timeout_ms=immowelt_config.get("timeout_ms", 20_000),
                    throttle_seconds=immowelt_config.get("throttle_seconds", 2.0),
                    language=language,
                )
            )
        except ImportError:
            LOGGER.error("Immowelt adapter enabled but could not be imported.")
            raise

    if not adapters:
        raise ValueError("No adapters enabled. Enable demo or immowelt in the config file.")

    filter_engine = FilterEngine(profile, language=language)
    database = ApartmentDatabase(load_database_path(config))
    notifier = Notifier(config, language=language)

    return ApartmentSearchRunner(
        adapters=adapters,
        filter_engine=filter_engine,
        database=database,
        notifier=notifier,
        language=language,
    )


def main() -> None:
    """Run the command-line interface for the apartment search agent."""
    parser = argparse.ArgumentParser(description="Apartment search agent")
    parser.add_argument("--config", default="config/search_profile.yml")
    parser.add_argument("--once", action="store_true", help="Run once and exit")
    parser.add_argument("--interval-minutes", type=int, default=60)
    args = parser.parse_args()

    runner = build_runner(args.config)

    if args.once:
        runner.run_once()
        return

    scheduler = BlockingScheduler()
    scheduler.add_job(runner.run_once, "interval", minutes=args.interval_minutes, next_run_time=None)
    LOGGER.info("Apartment agent running with interval: %s minutes", args.interval_minutes)
    scheduler.start()


if __name__ == "__main__":
    main()
