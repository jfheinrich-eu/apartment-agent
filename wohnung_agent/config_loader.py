from __future__ import annotations

from pathlib import Path
from typing import Any
import yaml
from wohnung_agent.models import SearchProfile


def load_config(config_path: str | Path) -> dict[str, Any]:
    with Path(config_path).open("r", encoding="utf-8") as config_file:
        config = yaml.safe_load(config_file)
    if not isinstance(config, dict):
        raise ValueError("Config file must contain a YAML object.")
    return config


def load_search_profile(config: dict[str, Any]) -> SearchProfile:
    return SearchProfile(
        max_warm_rent=config["max_warm_rent"],
        min_rooms=config["min_rooms"],
        kitchen_required=config.get("kitchen_required", True),
        regions=config["regions"],
    )
