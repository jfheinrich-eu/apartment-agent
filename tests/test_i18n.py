from apartment_agent.i18n import tr


def test_tr_falls_back_to_default_language_and_key():
    # Unknown language should fall back to English translation map
    assert tr("fr", "notifier.unknown") == "unknown"
    # Unknown key should return the key string itself
    assert tr("en", "non.existing.translation.key") == "non.existing.translation.key"