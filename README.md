# Wohnung Agent v1

A personal apartment search agent with adapter architecture, SQLite database, and notifications.

## Installation

### Basic installation (demo adapter only)

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -e .
cp config/search_profile.example.yml config/search_profile.yml
wohnung-agent --config config/search_profile.yml --once
```

### Full development setup

For tests and tooling:

```bash
pip install -e ".[dev]"
```

## Configuration

Edit `config/search_profile.yml` to configure:

- **Search criteria**: `max_warm_rent`, `min_rooms`, `kitchen_required`, `regions`
- **Adapters**: `demo` (test data), `immowelt` (web scraping)
- **Notifications**: `telegram`, `email` (optional)

### Immowelt Adapter

The Immowelt adapter works with manually configured search URLs from your browser.
This is intentional: Portal URLs and filter parameters change frequently.

**How to set up:**

1. Open Immowelt.de in your browser
2. Set region and filters: Price, rooms, "Wohnung mieten" (rent)
3. Copy the resulting URL
4. Add it to `config/search_profile.yml` under `immowelt.search_urls`:

```yaml
immowelt:
  enabled: true
  headless: true
  timeout_ms: 20000
  throttle_seconds: 2.0
  search_urls:
    - url: "https://www.immowelt.de/suche/boizenburg-elbe/wohnungen/mieten"
      city_hint: "Boizenburg"
    - url: "https://www.immowelt.de/suche/lueneburg/wohnungen/mieten"
      city_hint: "Lüneburg"
```

**Configuration options:**

- `enabled`: Whether to enable this adapter
- `search_urls`: List of Immowelt search result URLs (required)
- `headless`: Run browser headless (faster, no window)
- `timeout_ms`: Page load timeout in milliseconds
- `throttle_seconds`: Delay between requests (be respectful to the server)

## Usage

### One-time search

```bash
wohnung-agent --config config/search_profile.yml --once
```

### Scheduled search (every 60 minutes by default)

```bash
wohnung-agent --config config/search_profile.yml
```

### Custom interval

```bash
wohnung-agent --config config/search_profile.yml --interval-minutes 30
```

## Using make

Convenient commands via Makefile:

```bash
make dev-install    # Install with all dependencies
make test           # Run tests
make run-once       # Run one search cycle
make run            # Start scheduled runner
make clean          # Clean caches
```

See `make help` for all available targets.

## Project structure

- `wohnung_agent/` - Main package
  - `adapters/` - Data source adapters
    - `base.py` - Base adapter interface
    - `demo_adapter.py` - Test data
    - `immowelt_adapter.py` - Immowelt web scraper
  - `models.py` - Data models
  - `filter_engine.py` - Apartment scoring and filtering
  - `database.py` - SQLite persistence
  - `runner.py` - Search orchestration
  - `notifier.py` - Telegram/email notifications
  - `main.py` - CLI entry point
- `tests/` - Unit tests
- `config/` - Configuration files

## Limitations

- No guarantee that every listing is fully recognized
- Warm rent, rooms, and built-in kitchen are extracted from visible text
- Vodafone Cable 1000 is only reliably checkable with a complete address
- Portal changes only require adapter updates, not system changes

## Development

All tests pass:

```bash
make test
```

Python 3.11+, all dependencies in `pyproject.toml`.
