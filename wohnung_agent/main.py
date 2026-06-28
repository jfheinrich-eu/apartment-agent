from __future__ import annotations

import argparse
import logging
from pathlib import Path
from apscheduler.schedulers.blocking import BlockingScheduler
from wohnung_agent.adapters.demo_adapter import DemoAdapter
from wohnung_agent.config_loader import load_config, load_database_path, load_language, load_search_profile
from wohnung_agent.database import ApartmentDatabase
from wohnung_agent.filter_engine import FilterEngine
from wohnung_agent.i18n import tr
from wohnung_agent.notifier import Notifier
from wohnung_agent.reporting import generate_open_apartments_markdown
from wohnung_agent.runner import ApartmentSearchRunner

LOGGER = logging.getLogger(__name__)


def build_runner(config_path: str) -> ApartmentSearchRunner:
    """Create a fully configured runner from the YAML configuration."""
    config = load_config(config_path)
    language = load_language(config)
    profile = load_search_profile(config)

    adapters = []

    if config.demo.enabled:
        adapters.append(DemoAdapter())

    if config.immowelt.enabled:
        try:
            from wohnung_agent.adapters.immowelt_adapter import ImmoweltAdapter
            # Convert ImmoweltSearchUrlConfig objects to dicts for adapter compatibility
            search_urls = [
                {"url": item.url, "city_hint": item.city_hint}
                if hasattr(item, "url")
                else item
                for item in config.immowelt.search_urls
            ]
            adapters.append(
                ImmoweltAdapter(
                    search_urls=search_urls,
                    timeout_ms=config.immowelt.timeout_ms,
                    throttle_seconds=config.immowelt.throttle_seconds,
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
    # Configure logging at startup for consistent output across all execution modes.
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        force=True,
    )
    
    parser = argparse.ArgumentParser(description="Apartment search agent")
    parser.add_argument("--config", default="config/search_profile.yml")
    parser.add_argument("--once", action="store_true", help="Run once and exit")
    parser.add_argument("--interval-minutes", type=int, default=60)
    parser.add_argument("--report-open", action="store_true", help="Print markdown report of open apartments")
    parser.add_argument("--open-days", type=int, default=7, help="Open if seen in the last N days")
    parser.add_argument("--report-output", help="Optional markdown file path for report output")
    parser.add_argument("--delete-key", help="Delete one apartment by unique key")
    parser.add_argument("--delete-older-than-days", type=int, help="Delete apartments older than N days")
    args = parser.parse_args()

    if args.open_days < 0:
        parser.error("--open-days must be >= 0")
    if args.delete_older_than_days is not None and args.delete_older_than_days < 0:
        parser.error("--delete-older-than-days must be >= 0")

    management_mode = any(
        [
            args.report_open,
            args.report_output,
            args.delete_key,
            args.delete_older_than_days is not None,
        ]
    )

    if management_mode:
        config = load_config(args.config)
        language = load_language(config)
        db_path = load_database_path(config)

        with ApartmentDatabase(db_path) as database:
            if args.delete_key:
                deleted = database.delete_apartment(args.delete_key)
                if deleted:
                    print(tr(language, "db.delete_key_deleted", unique_key=args.delete_key))
                else:
                    print(tr(language, "db.delete_key_missing", unique_key=args.delete_key))

            if args.delete_older_than_days is not None:
                deleted_count = database.delete_apartments_older_than_days(args.delete_older_than_days)
                print(
                    tr(
                        language,
                        "db.delete_older_deleted",
                        days=args.delete_older_than_days,
                        count=deleted_count,
                    )
                )

            if args.report_open:
                apartments = database.get_open_apartments(args.open_days)
                report = generate_open_apartments_markdown(
                    apartments=apartments,
                    open_days=args.open_days,
                    language=language,
                )
                print(report)

                if args.report_output:
                    report_output_path = Path(args.report_output)
                    report_output_path.write_text(report, encoding="utf-8")
                    print(tr(language, "report.saved", path=str(report_output_path.resolve())))

        return

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
