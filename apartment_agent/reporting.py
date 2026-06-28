from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from apartment_agent.i18n import tr


def _stringify(value: Any, default: str) -> str:
    if value is None:
        return default
    return str(value)


def _escape_markdown(value: str) -> str:
    return value.replace("|", "\\|").replace("\n", " ").strip()


def _format_decimal(value: Any, default: str, digits: int = 1) -> str:
    if value is None:
        return default
    return f"{float(value):.{digits}f}"


def generate_open_apartments_markdown(
    apartments: list[dict[str, Any]],
    open_days: int,
    language: str = "en",
) -> str:
    """Render a markdown report for open apartments."""
    unknown_value = tr(language, "notifier.unknown")
    generated_at = datetime.now(timezone.utc).isoformat()

    lines = [
        f"# {tr(language, 'report.title')}",
        "",
        f"- {tr(language, 'report.generated_at')}: {generated_at}",
        f"- {tr(language, 'report.open_days', days=open_days)}",
        f"- {tr(language, 'report.count', count=len(apartments))}",
        "",
    ]

    if not apartments:
        lines.append(tr(language, "report.none"))
        return "\n".join(lines)

    lines.extend(
        [
            "| "
            + " | ".join(
                [
                    tr(language, "report.header.unique_key"),
                    tr(language, "report.header.city"),
                    tr(language, "report.header.title"),
                    tr(language, "report.header.rent"),
                    tr(language, "report.header.rooms"),
                    tr(language, "report.header.score"),
                    tr(language, "report.header.found_at"),
                    tr(language, "report.header.last_seen_at"),
                    tr(language, "report.header.url"),
                ]
            )
            + " |",
            "| --- | --- | --- | --- | --- | --- | --- | --- | --- |",
        ]
    )

    for apartment in apartments:
        lines.append(
            "| "
            + " | ".join(
                [
                    _escape_markdown(_stringify(apartment.get("unique_key"), unknown_value)),
                    _escape_markdown(_stringify(apartment.get("city"), unknown_value)),
                    _escape_markdown(_stringify(apartment.get("title"), unknown_value)),
                    _escape_markdown(_format_decimal(apartment.get("warm_rent_eur"), unknown_value)),
                    _escape_markdown(_format_decimal(apartment.get("rooms"), unknown_value)),
                    _escape_markdown(_stringify(apartment.get("score"), unknown_value)),
                    _escape_markdown(_stringify(apartment.get("found_at"), unknown_value)),
                    _escape_markdown(_stringify(apartment.get("last_seen_at"), unknown_value)),
                    _escape_markdown(_stringify(apartment.get("url"), unknown_value)),
                ]
            )
            + " |"
        )

    return "\n".join(lines)
