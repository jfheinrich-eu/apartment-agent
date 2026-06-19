# Wohnung Agent – Version 1

Ein schlanker Python-Agent für Wohnungssuche mit Adapter-Struktur, SQLite-Datenbank, Filterlogik und Benachrichtigung.

## Installation

```bash
cd wohnung_agent
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -e .
cp config/search_profile.example.yml config/search_profile.yml
```

## Start

```bash
wohnung-agent --config config/search_profile.yml --once
```

## Struktur

- `wohnung_agent/models.py` – Datenmodelle
- `wohnung_agent/filter_engine.py` – Pflichtfilter und Scoring
- `wohnung_agent/database.py` – SQLite-Speicherung und Duplikaterkennung
- `wohnung_agent/notifier.py` – Telegram/E-Mail-Ausgabe
- `wohnung_agent/adapters/` – Portal-Adapter
- `wohnung_agent/main.py` – Einstiegspunkt

## Hinweis

Die Beispiel-Adapter sind absichtlich konservativ. Für echte Portale solltest du bevorzugt offizielle APIs, RSS, gespeicherte Suchaufträge oder erlaubte Exportwege nutzen. Webseiten-Scraping kann gegen Nutzungsbedingungen verstoßen oder schnell brechen.
