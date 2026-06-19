from __future__ import annotations

import argparse
from apscheduler.schedulers.blocking import BlockingScheduler
from wohnung_agent.adapters.demo_adapter import DemoAdapter
from wohnung_agent.config_loader import load_config, load_search_profile
from wohnung_agent.database import ApartmentDatabase
from wohnung_agent.filter_engine import FilterEngine
from wohnung_agent.notifier import Notifier
from wohnung_agent.runner import ApartmentSearchRunner


def build_runner(config_path: str) -> ApartmentSearchRunner:
    config = load_config(config_path)
    profile = load_search_profile(config)

    adapters = [DemoAdapter()]
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
