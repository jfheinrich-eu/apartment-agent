from __future__ import annotations

from wohnung_agent.adapters.base import ApartmentAdapter
from wohnung_agent.database import ApartmentDatabase
from wohnung_agent.filter_engine import FilterEngine
from wohnung_agent.notifier import Notifier


class ApartmentSearchRunner:
    """
    Orchestrates the apartment search workflow:
    1. Fetch apartments from all adapters using adapter.search(profile)
    2. Evaluate each apartment using the filter engine
    3. Check for duplicates in the database
    4. Save new matches and notify if configured
    """

    def __init__(
        self,
        adapters: list[ApartmentAdapter],
        filter_engine: FilterEngine,
        database: ApartmentDatabase,
        notifier: Notifier,
    ) -> None:
        self.adapters = adapters
        self.filter_engine = filter_engine
        self.database = database
        self.notifier = notifier

    def run_once(self) -> None:
        """Execute one complete search cycle across all adapters."""
        print("Starte Wohnungssuche...")

        for adapter in self.adapters:
            print(f"Adapter: {adapter.__class__.__name__}")

            # All adapters must implement: search(profile: SearchProfile) -> list[Apartment]
            apartments = adapter.search(self.filter_engine.profile)
            print(f"Gefundene Roh-Treffer: {len(apartments)}")

            for apartment in apartments:
                print(
                    f"Prüfe: {apartment.title} | {apartment.warm_rent_eur} € | {apartment.rooms} Zimmer"
                )

                # Evaluate apartment against search profile
                match = self.filter_engine.evaluate(apartment)
                print(f"Score: {match.score}, Rejected: {match.rejected}")
                print(f"Gründe: {', '.join(match.reasons)}")

                # Skip rejected apartments
                if match.rejected:
                    continue

                # Skip duplicates
                if self.database.exists(apartment):
                    print("Schon bekannt.")
                    continue

                # Save new match and notify
                self.database.save_match(match)
                print(f"NEUER TREFFER: {apartment.title}")
                self.notifier.send(match)
