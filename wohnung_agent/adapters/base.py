from __future__ import annotations

from abc import ABC, abstractmethod
from wohnung_agent.models import Apartment, SearchProfile


class ApartmentAdapter(ABC):
    source_name: str

    @abstractmethod
    def search(self, profile: SearchProfile) -> list[Apartment]:
        """Return apartments from this source."""
