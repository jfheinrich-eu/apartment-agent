from __future__ import annotations

import locale
from typing import Any

DEFAULT_LANGUAGE = "en"
SUPPORTED_LANGUAGES = {"en", "de"}

TRANSLATIONS: dict[str, dict[str, str]] = {
    "en": {
        "runner.starting_search": "Starting apartment search",
        "runner.adapter": "Adapter: {adapter}",
        "runner.raw_found": "Raw apartments found: {count}",
        "runner.evaluating": "Evaluating apartment: {title} | {rent} EUR | {rooms} rooms",
        "runner.score": "Score: {score}, Rejected: {rejected}",
        "runner.reasons": "Reasons: {reasons}",
        "runner.already_known": "Already known",
        "runner.new_match": "New apartment match: {title}",
        "filter.city_mismatch": "City does not match: {city}",
        "filter.city_match": "City matches: {city}",
        "filter.rent_missing": "Warm rent missing",
        "filter.rent_match": "Warm rent matches: {rent:.0f} EUR",
        "filter.rent_too_high": "Warm rent too high: {rent:.0f} EUR",
        "filter.rooms_missing": "Room count missing",
        "filter.rooms_match": "Rooms match: {rooms}",
        "filter.rooms_too_few": "Too few rooms: {rooms}",
        "filter.kitchen_yes": "Built-in kitchen available",
        "filter.kitchen_no": "No built-in kitchen",
        "filter.kitchen_unknown": "Built-in kitchen unclear",
        "filter.address_available": "Address available",
        "filter.address_missing": "Address missing; internet check cannot be verified reliably",
        "filter.internet_yes": "Vodafone Cable 1000 available",
        "filter.internet_no": "Vodafone Cable 1000 not available",
        "filter.internet_unknown": "Vodafone Cable 1000 not checked",
        "notifier.new_match": "NEW MATCH: {city} - {title}",
        "notifier.rent": "Rent: {rent}",
        "notifier.rooms": "Rooms: {rooms}",
        "notifier.score": "Score: {score}/100",
        "notifier.link": "Link: {url}",
        "notifier.evaluation": "Evaluation:\n{reasons}",
        "notifier.unknown": "unknown",
        "text.unknown_city": "Unknown",
        "report.title": "Open apartments report",
        "report.generated_at": "Generated at",
        "report.open_days": "Open in the last {days} days",
        "report.count": "Apartments: {count}",
        "report.none": "No open apartments found.",
        "report.saved": "Report written to: {path}",
        "report.header.unique_key": "Unique key",
        "report.header.city": "City",
        "report.header.title": "Title",
        "report.header.rent": "Rent (EUR)",
        "report.header.rooms": "Rooms",
        "report.header.score": "Score",
        "report.header.found_at": "Found at",
        "report.header.last_seen_at": "Last seen at",
        "report.header.url": "URL",
        "db.delete_key_deleted": "Deleted apartment: {unique_key}",
        "db.delete_key_missing": "No apartment found for key: {unique_key}",
        "db.delete_older_deleted": "Deleted apartments older than {days} days: {count}",
    },
    "de": {
        "runner.starting_search": "Starte Wohnungssuche",
        "runner.adapter": "Adapter: {adapter}",
        "runner.raw_found": "Gefundene Roh-Treffer: {count}",
        "runner.evaluating": "Pruefe Wohnung: {title} | {rent} EUR | {rooms} Zimmer",
        "runner.score": "Score: {score}, Rejected: {rejected}",
        "runner.reasons": "Gruende: {reasons}",
        "runner.already_known": "Schon bekannt",
        "runner.new_match": "Neuer Treffer: {title}",
        "filter.city_mismatch": "Ort passt nicht: {city}",
        "filter.city_match": "Ort passt: {city}",
        "filter.rent_missing": "Warmmiete fehlt",
        "filter.rent_match": "Warmmiete passt: {rent:.0f} EUR",
        "filter.rent_too_high": "Warmmiete zu hoch: {rent:.0f} EUR",
        "filter.rooms_missing": "Zimmerzahl fehlt",
        "filter.rooms_match": "Zimmer passen: {rooms}",
        "filter.rooms_too_few": "Zu wenige Zimmer: {rooms}",
        "filter.kitchen_yes": "Einbaukueche vorhanden",
        "filter.kitchen_no": "Keine Einbaukueche",
        "filter.kitchen_unknown": "Einbaukueche ungeklaert",
        "filter.address_available": "Adresse vorhanden",
        "filter.address_missing": "Adresse fehlt; Internetpruefung nicht sicher moeglich",
        "filter.internet_yes": "Vodafone Kabel 1000 verfuegbar",
        "filter.internet_no": "Vodafone Kabel 1000 nicht verfuegbar",
        "filter.internet_unknown": "Vodafone Kabel 1000 ungeprueft",
        "notifier.new_match": "NEUER TREFFER: {city} - {title}",
        "notifier.rent": "Miete: {rent}",
        "notifier.rooms": "Zimmer: {rooms}",
        "notifier.score": "Score: {score}/100",
        "notifier.link": "Link: {url}",
        "notifier.evaluation": "Bewertung:\n{reasons}",
        "notifier.unknown": "unbekannt",
        "text.unknown_city": "Unbekannt",
        "report.title": "Report offener Wohnungen",
        "report.generated_at": "Erstellt am",
        "report.open_days": "Offen in den letzten {days} Tagen",
        "report.count": "Wohnungen: {count}",
        "report.none": "Keine offenen Wohnungen gefunden.",
        "report.saved": "Report geschrieben nach: {path}",
        "report.header.unique_key": "Unique key",
        "report.header.city": "Stadt",
        "report.header.title": "Titel",
        "report.header.rent": "Miete (EUR)",
        "report.header.rooms": "Zimmer",
        "report.header.score": "Score",
        "report.header.found_at": "Gefunden am",
        "report.header.last_seen_at": "Zuletzt gesehen am",
        "report.header.url": "URL",
        "db.delete_key_deleted": "Wohnung geloescht: {unique_key}",
        "db.delete_key_missing": "Keine Wohnung fuer key gefunden: {unique_key}",
        "db.delete_older_deleted": "Wohnungen aelter als {days} Tage geloescht: {count}",
    },
}


def resolve_language(config: dict[str, Any]) -> str:
    configured = str(config.get("language", "")).strip().casefold()
    if configured in SUPPORTED_LANGUAGES:
        return configured

    system_locale = (locale.getdefaultlocale()[0] or "").casefold()
    if system_locale.startswith("de"):
        return "de"
    if system_locale.startswith("en"):
        return "en"

    return DEFAULT_LANGUAGE


def tr(language: str, key: str, **kwargs: Any) -> str:
    language_map = TRANSLATIONS.get(language, TRANSLATIONS[DEFAULT_LANGUAGE])
    template = language_map.get(key, TRANSLATIONS[DEFAULT_LANGUAGE].get(key, key))
    return template.format(**kwargs)
