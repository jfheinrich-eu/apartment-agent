from __future__ import annotations

import logging

from wohnung_agent.adapters.base import ApartmentAdapter
from wohnung_agent.database import ApartmentDatabase
from wohnung_agent.filter_engine import FilterEngine
from wohnung_agent.i18n import tr
from wohnung_agent.notifier import Notifier

LOGGER = logging.getLogger(__name__)


class ApartmentSearchRunner:
    """Coordinate adapters, scoring, persistence, and notifications."""

    def __init__(
        self,
        adapters: list[ApartmentAdapter],
        filter_engine: FilterEngine,
        database: ApartmentDatabase,
        notifier: Notifier,
        language: str = "en",
    ) -> None:
        """Store the dependencies that drive a single search cycle."""
        self.adapters = adapters
        self.filter_engine = filter_engine
        self.database = database
        self.notifier = notifier
        self.language = language

    def run_once(self) -> None:
        """Execute one complete search cycle across all adapters."""
        LOGGER.info(tr(self.language, "runner.starting_search"))

        for adapter in self.adapters:
            LOGGER.info(tr(self.language, "runner.adapter", adapter=adapter.__class__.__name__))

            # All adapters must implement: search(profile: SearchProfile) -> list[Apartment]
            apartments = adapter.search(self.filter_engine.profile)
            LOGGER.info(tr(self.language, "runner.raw_found", count=len(apartments)))

            for apartment in apartments:
                LOGGER.info(
                    tr(
                        self.language,
                        "runner.evaluating",
                        title=apartment.title,
                        rent=apartment.warm_rent_eur,
                        rooms=apartment.rooms,
                    )
                )

                # Evaluate apartment against search profile
                apartment_match = self.filter_engine.evaluate(apartment)
                LOGGER.info(
                    tr(
                        self.language,
                        "runner.score",
                        score=apartment_match.score,
                        rejected=apartment_match.rejected,
                    )
                )
                LOGGER.info(tr(self.language, "runner.reasons", reasons=", ".join(apartment_match.reasons)))

                # Skip rejected apartments
                if apartment_match.rejected:
                    continue

                # Skip duplicates
                if self.database.exists(apartment):
                    LOGGER.info(tr(self.language, "runner.already_known"))
                    continue

                # Save new match and notify
                self.database.save_match(apartment_match)
                LOGGER.info(tr(self.language, "runner.new_match", title=apartment.title))
                self.notifier.send(apartment_match)
