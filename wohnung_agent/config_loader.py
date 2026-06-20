from __future__ import annotations

from pathlib import Path
from typing import Any
import yaml

from wohnung_agent.i18n import resolve_language
from wohnung_agent.models import SearchProfile


def load_config(config_path: str | Path) -> dict[str, Any]:
    """Load and validate the YAML configuration file."""
    resolved = Path(config_path).resolve()
    if not resolved.is_file():
        raise FileNotFoundError(f"Config file not found: {resolved}")
    with resolved.open("r", encoding="utf-8") as config_file:
        config = yaml.safe_load(config_file)
    if not isinstance(config, dict):
        raise ValueError("Config file must contain a YAML object.")
    return config


def load_search_profile(config: dict[str, Any]) -> SearchProfile:
    """Build the typed search profile from top-level config values."""
    required_keys = ["max_warm_rent", "min_rooms", "regions"]
    missing_keys = [key for key in required_keys if key not in config]
    if missing_keys:
        missing = ", ".join(missing_keys)
        raise ValueError(f"Missing required config keys for search profile: {missing}")

    return SearchProfile(
        max_warm_rent=config["max_warm_rent"],
        min_rooms=config["min_rooms"],
        kitchen_required=config.get("kitchen_required", True),
        regions=config["regions"],
    )


def load_database_path(config: dict[str, Any]) -> str:
    """Return the configured database path or the default SQLite file."""
    return str(config.get("database_path", "wohnungen.sqlite3"))


def load_language(config: dict[str, Any]) -> str:
    """Resolve UI language from config, then system locale, then English fallback."""
    return resolve_language(config)
