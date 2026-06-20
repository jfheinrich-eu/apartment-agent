from pathlib import Path

import pytest

from wohnung_agent.config_loader import load_config, load_database_path, load_language, load_search_profile
from unittest.mock import patch


def test_load_search_profile_raises_on_missing_required_keys():
    config = {"min_rooms": 2.5, "regions": ["Boizenburg"]}

    try:
        load_search_profile(config)
        raise AssertionError("Expected ValueError for missing keys")
    except ValueError as error:
        assert "max_warm_rent" in str(error)


def test_load_language_uses_config_value_when_supported():
    assert load_language({"language": "de"}) == "de"
    assert load_language({"language": "en"}) == "en"


def test_load_language_falls_back_to_system_locale_de():
    with patch("wohnung_agent.i18n.locale.getdefaultlocale", return_value=("de_DE", "UTF-8")):
        assert load_language({}) == "de"


def test_load_language_falls_back_to_system_locale_en():
    with patch("wohnung_agent.i18n.locale.getdefaultlocale", return_value=("en_US", "UTF-8")):
        assert load_language({}) == "en"


def test_load_language_uses_english_default_for_unknown_locale():
    with patch("wohnung_agent.i18n.locale.getdefaultlocale", return_value=("fr_FR", "UTF-8")):
        assert load_language({}) == "en"


def test_load_config_raises_for_missing_file(tmp_path):
    missing_path = tmp_path / "missing.yml"
    with pytest.raises(FileNotFoundError):
        load_config(missing_path)


def test_load_config_raises_for_non_mapping_yaml(tmp_path):
    config_path = tmp_path / "invalid.yml"
    config_path.write_text("- not\n- a\n- mapping\n", encoding="utf-8")

    with pytest.raises(ValueError):
        load_config(config_path)


def test_load_config_returns_mapping(tmp_path):
    config_path = tmp_path / "valid.yml"
    config_path.write_text("max_warm_rent: 800\nmin_rooms: 2.5\nregions: [Boizenburg]\n", encoding="utf-8")

    loaded = load_config(config_path)
    assert isinstance(loaded, dict)
    assert loaded["max_warm_rent"] == 800


def test_load_database_path_default_and_override():
    assert load_database_path({}) == "wohnungen.sqlite3"
    assert load_database_path({"database_path": "custom.sqlite3"}) == "custom.sqlite3"