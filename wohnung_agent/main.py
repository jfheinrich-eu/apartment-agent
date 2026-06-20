from __future__ import annotations

import argparse
from apscheduler.schedulers.blocking import BlockingScheduler
from wohnung_agent.adapters.demo_adapter import DemoAdapter
# from wohnung_agent.adapters.immowelt_adapter import ImmoweltAdapter
from wohnung_agent.config_loader import load_config, load_search_profile
from wohnung_agent.database import ApartmentDatabase
from wohnung_agent.filter_engine import FilterEngine
from wohnung_agent.notifier import Notifier
from wohnung_agent.runner import ApartmentSearchRunner


def build_runner(config_path: str) -> ApartmentSearchRunner:
    config = load_config(config_path)
    profile = load_search_profile(config)

    adapters = []

    if config.get("demo", {}).get("enabled", False):
        adapters.append(DemoAdapter())

    immowelt_config = config.get("immowelt", {})
    if immowelt_config.get("enabled", False):
        adapters.append(
            ImmoweltAdapter(
                search_urls=immowelt_config.get("search_urls", []),
                headless=immowelt_config.get("headless", True),
                timeout_ms=immowelt_config.get("timeout_ms", 20_000),
                throttle_seconds=immowelt_config.get("throttle_seconds", 2.0),
            )
        )

    if not adapters:
        raise ValueError("No adapters enabled. Enable demo or immowelt in the config file.")
    filter_engine = FilterEngine(profile)
    database = ApartmentDatabase("wohnungen.sqlite3")
    notifier = Notifier(config)

    return ApartmentSearchRunner(
        adapters=adapters,
        filter_engine=filter_engine,
        database=database,
        notifier=notifier,
    )


def main() -> None:
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
    print(f"Wohnung-Agent läuft. Intervall: {args.interval_minutes} Minuten")
    scheduler.start()


if __name__ == "__main__":
    main()
