from pathlib import Path

import pytest

from apartment_agent.config_loader import load_config, load_database_path, load_language, load_search_profile
from apartment_agent.models import AppConfig
from unittest.mock import patch


def test_load_config_returns_app_config_instance(tmp_path):
    """Test that load_config returns a fully validated AppConfig instance."""
    config_path = tmp_path / "valid.yml"
    config_path.write_text(
        "max_warm_rent: 800\nmin_rooms: 2.5\nregions:\n  - Boizenburg\n",
        encoding="utf-8",
    )
    loaded = load_config(config_path)
    assert isinstance(loaded, AppConfig)
    assert loaded.max_warm_rent == 800
    assert loaded.min_rooms == 2.5
    assert loaded.regions == ["Boizenburg"]


def test_load_config_raises_for_invalid_max_warm_rent(tmp_path):
    """Test that load_config validates max_warm_rent > 0."""
    config_path = tmp_path / "invalid_rent.yml"
    config_path.write_text(
        "max_warm_rent: 0\nmin_rooms: 2.5\nregions:\n  - Boizenburg\n",
        encoding="utf-8",
    )
    with pytest.raises(ValueError, match="max_warm_rent must be > 0"):
        load_config(config_path)


def test_load_config_raises_for_negative_min_rooms(tmp_path):
    """Test that load_config validates min_rooms >= 0."""
    config_path = tmp_path / "invalid_rooms.yml"
    config_path.write_text(
        "max_warm_rent: 800\nmin_rooms: -1\nregions:\n  - Boizenburg\n",
        encoding="utf-8",
    )
    with pytest.raises(ValueError, match="min_rooms must be >= 0"):
        load_config(config_path)


def test_load_config_raises_for_empty_regions(tmp_path):
    """Test that load_config validates regions is not empty."""
    config_path = tmp_path / "no_regions.yml"
    config_path.write_text(
        "max_warm_rent: 800\nmin_rooms: 2.5\nregions: []\n",
        encoding="utf-8",
    )
    with pytest.raises(ValueError, match="regions must be a non-empty list"):
        load_config(config_path)


def test_load_config_raises_for_invalid_language(tmp_path):
    """Test that load_config validates language is 'en' or 'de'."""
    config_path = tmp_path / "bad_language.yml"
    config_path.write_text(
        "max_warm_rent: 800\nmin_rooms: 2.5\nregions:\n  - Boizenburg\nlanguage: fr\n",
        encoding="utf-8",
    )
    with pytest.raises(ValueError, match="language must be 'en' or 'de'"):
        load_config(config_path)


def test_load_config_raises_for_invalid_smtp_port(tmp_path):
    """Test that load_config validates SMTP port is in valid range."""
    config_path = tmp_path / "bad_smtp_port.yml"
    config_path.write_text(
        "max_warm_rent: 800\nmin_rooms: 2.5\nregions:\n  - Boizenburg\n"
        "email:\n  smtp_port: 99999\n",
        encoding="utf-8",
    )
    with pytest.raises(ValueError, match="SMTP port must be between"):
        load_config(config_path)


def test_load_config_raises_for_non_numeric_smtp_port(tmp_path):
    """Test that load_config reports a clear error for non-numeric smtp_port values."""
    config_path = tmp_path / "bad_smtp_port_type.yml"
    config_path.write_text(
        "max_warm_rent: 800\nmin_rooms: 2.5\nregions:\n  - Boizenburg\n"
        "email:\n  smtp_port: not-a-number\n",
        encoding="utf-8",
    )
    with pytest.raises(ValueError, match="smtp_port must be a numeric value"):
        load_config(config_path)


def test_load_config_raises_for_invalid_immowelt_timeout(tmp_path):
    """Test that load_config validates immowelt timeout_ms > 0."""
    config_path = tmp_path / "bad_timeout.yml"
    config_path.write_text(
        "max_warm_rent: 800\nmin_rooms: 2.5\nregions:\n  - Boizenburg\n"
        "immowelt:\n  timeout_ms: 0\n",
        encoding="utf-8",
    )
    with pytest.raises(ValueError, match="timeout_ms must be > 0"):
        load_config(config_path)


def test_load_search_profile_from_app_config():
    """Test that load_search_profile extracts SearchProfile from AppConfig."""
    config = AppConfig(
        max_warm_rent=800,
        min_rooms=2.5,
        kitchen_required=True,
        regions=["Boizenburg"],
    )
    profile = load_search_profile(config)
    assert profile.max_warm_rent == 800
    assert profile.min_rooms == 2.5
    assert profile.kitchen_required is True
    assert profile.regions == ["Boizenburg"]


def test_load_language_from_app_config():
    """Test that load_language extracts language from AppConfig."""
    config = AppConfig(
        max_warm_rent=800,
        min_rooms=2.5,
        regions=["Boizenburg"],
        language="de",
    )
    assert load_language(config) == "de"


def test_load_language_uses_locale_fallback_when_not_explicitly_set():
    """Test that omitted language falls back to locale resolution."""
    config = AppConfig(
        max_warm_rent=800,
        min_rooms=2.5,
        regions=["Boizenburg"],
    )
    with patch("apartment_agent.config_loader.resolve_language", return_value="de"):
        assert load_language(config) == "de"


def test_load_config_normalizes_language_values(tmp_path):
    """Test that language values are normalized for whitespace and case."""
    config_path = tmp_path / "language_normalized.yml"
    config_path.write_text(
        "max_warm_rent: 800\nmin_rooms: 2.5\nregions:\n  - Boizenburg\nlanguage: \" DE \"\n",
        encoding="utf-8",
    )
    loaded = load_config(config_path)
    assert loaded.language == "de"


def test_load_language_defaults_to_en():
    """Test that load_language falls back to English for unknown locales."""
    config = AppConfig(
        max_warm_rent=800,
        min_rooms=2.5,
        regions=["Boizenburg"],
        language="en",
    )
    assert load_language(config) == "en"


def test_load_database_path_from_app_config():
    """Test that load_database_path extracts database path from AppConfig."""
    config = AppConfig(
        max_warm_rent=800,
        min_rooms=2.5,
        regions=["Boizenburg"],
        database_path="custom.sqlite3",
    )
    assert load_database_path(config) == "custom.sqlite3"


def test_load_database_path_default():
    """Test that load_database_path returns default path when not configured."""
    config = AppConfig(
        max_warm_rent=800,
        min_rooms=2.5,
        regions=["Boizenburg"],
    )
    assert load_database_path(config) == "apartments.sqlite3"


def test_load_config_raises_for_missing_file(tmp_path):
    """Test that load_config raises FileNotFoundError for missing config file."""
    missing_path = tmp_path / "missing.yml"
    with pytest.raises(FileNotFoundError):
        load_config(missing_path)


def test_load_config_raises_for_non_mapping_yaml(tmp_path):
    """Test that load_config raises ValueError for non-mapping YAML."""
    config_path = tmp_path / "invalid.yml"
    config_path.write_text("- not\n- a\n- mapping\n", encoding="utf-8")

    with pytest.raises(ValueError):
        load_config(config_path)


def test_load_config_with_defaults(tmp_path):
    """Test that load_config applies all defaults correctly."""
    config_path = tmp_path / "minimal.yml"
    # Only required fields
    config_path.write_text(
        "max_warm_rent: 1000\nmin_rooms: 2\nregions:\n  - TestCity\n",
        encoding="utf-8",
    )
    config = load_config(config_path)
    
    # Check defaults
    assert config.language == "en"
    assert config.database_path == "apartments.sqlite3"
    assert config.kitchen_required is True
    assert config.demo.enabled is False
    assert config.immowelt.enabled is False
    assert config.telegram.enabled is False
    assert config.email.enabled is False