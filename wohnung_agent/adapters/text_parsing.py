from __future__ import annotations

import hashlib
import re
from urllib.parse import urlparse, parse_qs


def stable_id_from_url(url: str) -> str:
    parsed_url = urlparse(url)
    path = parsed_url.path.rstrip("/")

    # Common expose-id patterns. Keep this intentionally broad.
    match = re.search(r"([a-f0-9]{8,}[-a-f0-9]*|\d{6,})", path, re.IGNORECASE)
    if match:
        return match.group(1).lower()

    query_parameters = parse_qs(parsed_url.query)
    for key in ("id", "expose", "exposeId", "adId"):
        if key in query_parameters and query_parameters[key]:
            return query_parameters[key][0]

    return hashlib.sha256(url.encode("utf-8")).hexdigest()[:16]


def parse_german_number(value: str) -> float | None:
    normalized = value.replace(".", "").replace(",", ".")
    match = re.search(r"\d+(?:\.\d+)?", normalized)
    if not match:
        return None
    return float(match.group(0))


def parse_warm_rent(text: str) -> float | None:
    patterns = [
        r"(?:warmmiete|warm|gesamtmiete)\D{0,20}(\d[\d.]*,?\d*)\s*€",
        r"(\d[\d.]*,?\d*)\s*€\s*(?:warm|warmmiete|gesamtmiete)",
        r"(\d[\d.]*,?\d*)\s*€",
    ]
    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            return parse_german_number(match.group(1))
    return None


def parse_rooms(text: str) -> float | None:
    patterns = [
        r"(\d+(?:[,.]\d+)?)\s*(?:zimmer|zi\.?|räume)",
        r"zimmer\D{0,12}(\d+(?:[,.]\d+)?)",
    ]
    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            return parse_german_number(match.group(1))
    return None


def parse_living_area(text: str) -> float | None:
    patterns = [
        r"(\d+(?:[,.]\d+)?)\s*(?:m²|qm|m2)",
        r"wohnfläche\D{0,12}(\d+(?:[,.]\d+)?)",
    ]
    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            return parse_german_number(match.group(1))
    return None


def parse_has_kitchen(text: str) -> bool | None:
    normalized = text.casefold()
    positive_terms = ["einbauküche", "ebk", "küche vorhanden", "mit küche"]
    negative_terms = ["ohne einbauküche", "keine einbauküche", "ohne ebk", "keine ebk"]

    if any(term in normalized for term in negative_terms):
        return False
    if any(term in normalized for term in positive_terms):
        return True
    return None


def detect_city(text: str, regions: list[str], fallback: str | None = None) -> str:
    normalized = text.casefold()
    for region in regions:
        if region.casefold() in normalized:
            return region
    if fallback:
        return fallback
    return "Unbekannt"
