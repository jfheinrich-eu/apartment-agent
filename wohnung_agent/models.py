from __future__ import annotations

from datetime import datetime, timezone
from enum import Enum
from typing import Optional
from pydantic import BaseModel, HttpUrl, Field


class InternetStatus(str, Enum):
    UNKNOWN = "unknown"
    NOT_CHECKABLE = "not_checkable"
    AVAILABLE_1000 = "available_1000"
    NOT_AVAILABLE_1000 = "not_available_1000"


class Apartment(BaseModel):
    source: str
    external_id: str
    title: str
    url: HttpUrl
    city: str
    warm_rent_eur: Optional[float] = None
    rooms: Optional[float] = None
    living_area_sqm: Optional[float] = None
    has_kitchen: Optional[bool] = None
    address: Optional[str] = None
    internet_status: InternetStatus = InternetStatus.UNKNOWN
    found_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    @property
    def unique_key(self) -> str:
        return f"{self.source}:{self.external_id}"


class SearchProfile(BaseModel):
    max_warm_rent: float
    min_rooms: float
    kitchen_required: bool = True
    regions: list[str]


class ApartmentMatch(BaseModel):
    apartment: Apartment
    score: int
    reasons: list[str]
    rejected: bool = False
