from __future__ import annotations

from pathlib import Path
import yaml

from apartment_agent.i18n import resolve_language
from apartment_agent.models import AppConfig, SearchProfile


def load_config(config_path: str | Path) -> AppConfig:
    """Load and validate the YAML configuration file.
    
    Args:
        config_path: Path to the YAML configuration file.
    
    Returns:
        Fully validated AppConfig instance.
    
    Raises:
        FileNotFoundError: If the config file does not exist.
        ValueError: If the config file is not a valid YAML mapping.
        ValidationError: If the config fails Pydantic validation.
    """
    resolved = Path(config_path).resolve()
    if not resolved.is_file():
        raise FileNotFoundError(f"Config file not found: {resolved}")
    with resolved.open("r", encoding="utf-8") as config_file:
        config_dict = yaml.safe_load(config_file)
    if not isinstance(config_dict, dict):
        raise ValueError("Config file must contain a YAML object.")
    # Pydantic validation happens automatically here
    return AppConfig(**config_dict)


def load_search_profile(config: AppConfig) -> SearchProfile:
    """Build the typed search profile from AppConfig."""
    return SearchProfile(
        max_warm_rent=config.max_warm_rent,
        min_rooms=config.min_rooms,
        kitchen_required=config.kitchen_required,
        regions=config.regions,
    )


def load_database_path(config: AppConfig) -> str:
    """Return the configured database path or the default SQLite file."""
    return config.database_path


def load_language(config: AppConfig) -> str:
    """Resolve UI language from config, then system locale, then English fallback."""
    # Respect explicit config language; otherwise reuse locale fallback behavior.
    if "language" in config.model_fields_set:
        return config.language
    return resolve_language({})
