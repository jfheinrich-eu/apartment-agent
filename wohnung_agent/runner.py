from __future__ import annotations

import logging

from wohnung_agent.adapters.base import ApartmentAdapter
from wohnung_agent.database import ApartmentDatabase
from wohnung_agent.filter_engine import FilterEngine
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
    ) -> None:
        """Store the dependencies that drive a single search cycle."""
        self.adapters = adapters
        self.filter_engine = filter_engine
        self.database = database
        self.notifier = notifier

    def run_once(self) -> None:
        """Execute one complete search cycle across all adapters."""
        LOGGER.info("Starting apartment search")

        for adapter in self.adapters:
            LOGGER.info("Adapter: %s", adapter.__class__.__name__)

            # All adapters must implement: search(profile: SearchProfile) -> list[Apartment]
            apartments = adapter.search(self.filter_engine.profile)
            LOGGER.info("Raw apartments found: %s", len(apartments))

            for apartment in apartments:
                LOGGER.info(
                    "Evaluating apartment: %s | %s € | %s rooms",
                    apartment.title,
                    apartment.warm_rent_eur,
                    apartment.rooms,
                )

                # Evaluate apartment against search profile
                apartment_match = self.filter_engine.evaluate(apartment)
                LOGGER.info("Score: %s, Rejected: %s", apartment_match.score, apartment_match.rejected)
                LOGGER.info("Reasons: %s", ", ".join(apartment_match.reasons))

                # Skip rejected apartments
                if apartment_match.rejected:
                    continue

                # Skip duplicates
                if self.database.exists(apartment):
                    LOGGER.info("Already known")
                    continue

                # Save new match and notify
                self.database.save_match(apartment_match)
                LOGGER.info("New apartment match: %s", apartment.title)
                self.notifier.send(apartment_match)
