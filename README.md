# Wohnung Agent v1

Ein persönlicher Wohnungs-Suchagent mit Adapter-Struktur, SQLite-Datenbank und Benachrichtigung.

## Installation

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\\Scripts\\activate
pip install -e .
python -m playwright install chromium
cp config/search_profile.example.yml config/search_profile.yml
wohnung-agent --config config/search_profile.yml --once
```

## Immowelt-Adapter

Der Immowelt-Adapter arbeitet mit Such-URLs aus deiner Konfiguration.
Das ist absichtlich so. Portal-URLs, Location-IDs und Filterparameter ändern sich.

Empfehlung:

1. Immowelt im Browser öffnen.
2. Region setzen.
3. Filter setzen: Miete, Zimmer, Wohnung mieten.
4. Ergebnis-URL kopieren.
5. In `config/search_profile.yml` unter `immowelt.search_urls` eintragen.

Beispiel:

```yaml
immowelt:
  enabled: true
  headless: true
  search_urls:
    - url: "https://www.immowelt.de/suche/boizenburg-elbe/wohnungen/mieten"
      city_hint: "Boizenburg"
```

## Grenzen

- Keine Garantie, dass jedes Exposé vollständig erkannt wird.
- Warmmiete, Zimmer und EBK werden aus sichtbarem Kartentext extrahiert.
- Vodafone Kabel 1000 ist erst zuverlässig prüfbar, wenn eine vollständige Adresse vorliegt.
- Bei Portal-Änderungen muss nur der Adapter angepasst werden, nicht das Gesamtsystem.
