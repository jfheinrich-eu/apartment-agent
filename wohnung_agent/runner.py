from __future__ import annotations

from wohnung_agent.adapters.base import ApartmentAdapter
from wohnung_agent.database import ApartmentDatabase
from wohnung_agent.filter_engine import FilterEngine
from wohnung_agent.notifier import Notifier


class ApartmentSearchRunner:
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
        for adapter in self.adapters:
            apartments = adapter.search(self.filter_engine.profile)
            for apartment in apartments:
                apartment_match = self.filter_engine.evaluate(apartment)
                is_new = self.database.save_match(apartment_match)
                if is_new and not apartment_match.rejected:
                    self.notifier.send(apartment_match)
