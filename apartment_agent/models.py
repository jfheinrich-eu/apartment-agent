from __future__ import annotations

from datetime import datetime, timezone
from enum import Enum
from typing import Optional
from pydantic import BaseModel, HttpUrl, Field, field_validator


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


# Configuration models for YAML file validation

class ImmoweltSearchUrlConfig(BaseModel):
    """Represents a single Immowelt search URL configuration."""
    url: str
    city_hint: Optional[str] = None


class ImmoweltAdapterConfig(BaseModel):
    """Configuration for the Immowelt adapter."""
    enabled: bool = False
    search_urls: list[ImmoweltSearchUrlConfig | str] = Field(default_factory=list)
    timeout_ms: int = 20_000
    throttle_seconds: float = 2.0

    @field_validator("timeout_ms")
    @classmethod
    def validate_timeout_ms(cls, v: int) -> int:
        """Ensure timeout_ms is positive."""
        if v <= 0:
            raise ValueError("timeout_ms must be > 0")
        return v

    @field_validator("throttle_seconds")
    @classmethod
    def validate_throttle_seconds(cls, v: float) -> float:
        """Ensure throttle_seconds is non-negative."""
        if v < 0:
            raise ValueError("throttle_seconds must be >= 0")
        return v

    @field_validator("search_urls", mode="before")
    @classmethod
    def normalize_search_urls(cls, v):
        """Convert string URLs to ImmoweltSearchUrlConfig objects."""
        if not isinstance(v, list):
            return v
        normalized = []
        for item in v:
            if isinstance(item, str):
                normalized.append(ImmoweltSearchUrlConfig(url=item))
            elif isinstance(item, dict):
                normalized.append(ImmoweltSearchUrlConfig(**item))
            else:
                normalized.append(item)
        return normalized


class DemoAdapterConfig(BaseModel):
    """Configuration for the Demo adapter."""
    enabled: bool = False


class TelegramConfig(BaseModel):
    """Configuration for Telegram notifications."""
    enabled: bool = False
    bot_token: str = ""
    chat_id: str = ""


class EmailConfig(BaseModel):
    """Configuration for email notifications."""
    enabled: bool = False
    smtp_host: str = ""
    smtp_port: int = 587
    username: str = ""
    password: str = ""
    recipient: str = ""

    @field_validator("smtp_port", mode="before")
    @classmethod
    def validate_smtp_port(cls, v) -> int:
        """Ensure SMTP port is within valid range."""
        if isinstance(v, str):
            try:
                v = int(v)
            except ValueError as error:
                raise ValueError("smtp_port must be a numeric value") from error
        if not 1 <= v <= 65535:
            raise ValueError(f"SMTP port must be between 1 and 65535, got {v}")
        return v


class AppConfig(BaseModel):
    """Complete application configuration loaded from YAML."""
    # Required search criteria
    max_warm_rent: float
    min_rooms: float
    kitchen_required: bool = True
    regions: list[str]

    # Optional settings
    language: str = "en"
    database_path: str = "apartments.sqlite3"

    # Adapter configurations
    demo: DemoAdapterConfig = Field(default_factory=DemoAdapterConfig)
    immowelt: ImmoweltAdapterConfig = Field(default_factory=ImmoweltAdapterConfig)

    # Notification channels
    telegram: TelegramConfig = Field(default_factory=TelegramConfig)
    email: EmailConfig = Field(default_factory=EmailConfig)

    @field_validator("max_warm_rent")
    @classmethod
    def validate_max_rent(cls, v: float) -> float:
        """Ensure max_warm_rent is positive."""
        if v <= 0:
            raise ValueError("max_warm_rent must be > 0")
        return v

    @field_validator("min_rooms")
    @classmethod
    def validate_min_rooms(cls, v: float) -> float:
        """Ensure min_rooms is non-negative."""
        if v < 0:
            raise ValueError("min_rooms must be >= 0")
        return v

    @field_validator("regions")
    @classmethod
    def validate_regions(cls, v: list[str]) -> list[str]:
        """Ensure regions list is not empty."""
        if not v or not isinstance(v, list):
            raise ValueError("regions must be a non-empty list of strings")
        return v

    @field_validator("language")
    @classmethod
    def validate_language(cls, v: str) -> str:
        """Normalize language code."""
        normalized = v.strip().lower()
        if normalized not in ("en", "de"):
            raise ValueError(f"language must be 'en' or 'de', got '{v}'")
        return normalized
