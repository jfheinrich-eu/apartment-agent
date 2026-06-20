from __future__ import annotations

from wohnung_agent.adapters.base import ApartmentAdapter
from wohnung_agent.models import Apartment, SearchProfile


class DemoAdapter(ApartmentAdapter):
    """Return deterministic sample apartments for development and tests."""

    source_name = "demo"

    def search(self, profile: SearchProfile) -> list[Apartment]:
        """Return a stable demo dataset independent of the search profile."""
        return [
            Apartment(
                source=self.source_name,
                external_id="boizenburg-001",
                title="2,5 Zimmer mit Einbauküche in Boizenburg",
                url="https://example.com/boizenburg-001",
                city="Boizenburg",
                warm_rent_eur=760,
                rooms=2.5,
                living_area_sqm=68,
                has_kitchen=True,
                address=None,
            ),
            Apartment(
                source=self.source_name,
                external_id="lueneburg-001",
                title="Schöne Wohnung in Lüneburg, aber zu teuer",
                url="https://example.com/lueneburg-001",
                city="Lüneburg",
                warm_rent_eur=980,
                rooms=3,
                living_area_sqm=72,
                has_kitchen=True,
            ),
        ]
