from __future__ import annotations

import logging
import time
from dataclasses import dataclass
from numbers import Real
from typing import Any
from urllib.parse import urljoin

from bs4 import BeautifulSoup
import requests

from wohnung_agent.adapters.base import ApartmentAdapter
from wohnung_agent.adapters.text_parsing import (
    detect_city,
    parse_has_kitchen,
    parse_living_area,
    parse_rooms,
    parse_warm_rent,
    stable_id_from_url,
)
from wohnung_agent.models import Apartment, SearchProfile

LOGGER = logging.getLogger(__name__)


@dataclass(frozen=True)
class ImmoweltSearchUrl:
    url: str
    city_hint: str | None = None


class ImmoweltAdapter(ApartmentAdapter):
    """Adapter for Immowelt search result pages.

    This adapter expects manually prepared Immowelt search URLs in the YAML config.
    That is deliberate: Immowelt changes URL parameters and location ids over time.
    Copying a working browser search URL into the config is more stable than trying
    to guess the internal search URL format.
    """

    source_name = "immowelt"

    def __init__(
        self,
        search_urls: list[str | dict[str, str]],
        timeout_ms: int = 20_000,
        throttle_seconds: float = 2.0,
        language: str = "en",
    ) -> None:
        """Configure URL inputs, network timing, and output language."""
        if not isinstance(timeout_ms, Real) or isinstance(timeout_ms, bool):
            raise ValueError("timeout_ms must be a positive number")
        if timeout_ms <= 0:
            raise ValueError("timeout_ms must be positive")
        if not isinstance(throttle_seconds, Real) or isinstance(throttle_seconds, bool):
            raise ValueError("throttle_seconds must be a non-negative number")
        if throttle_seconds < 0:
            raise ValueError("throttle_seconds must be non-negative")

        self.search_urls = [self._normalize_search_url(item) for item in search_urls]
        self.timeout_ms = timeout_ms
        self.throttle_seconds = throttle_seconds
        self.language = language
        self._headers = {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/126.0 Safari/537.36"
            ),
            "Accept-Language": "de-DE,de;q=0.9,en;q=0.8",
        }

    def search(self, profile: SearchProfile) -> list[Apartment]:
        """Fetch configured search pages and extract apartment cards."""
        apartments: list[Apartment] = []

        if not self.search_urls:
            LOGGER.warning("No Immowelt search URLs configured.")
            return apartments

        session = requests.Session()
        session.max_redirects = 5

        try:
            for search_url in self.search_urls:
                try:
                    LOGGER.info("Loading Immowelt search URL: %s", search_url.url)
                    response = session.get(
                        search_url.url,
                        headers=self._headers,
                        timeout=max(1.0, self.timeout_ms / 1000.0),
                        allow_redirects=True,
                    )
                    response.raise_for_status()
                    apartments.extend(self._parse_html(response.text, search_url, profile))
                    time.sleep(self.throttle_seconds)
                except requests.Timeout as error:
                    LOGGER.warning("Immowelt timeout for %s: %s", search_url.url, error)
                except requests.ConnectionError as error:
                    LOGGER.warning("Immowelt connection error for %s: %s", search_url.url, error)
                except requests.RequestException as error:
                    LOGGER.warning("Immowelt request failed for %s: %s", search_url.url, error)
                except Exception as error:
                    LOGGER.exception("Immowelt adapter unexpected failure for %s: %s", search_url.url, error)
        finally:
            session.close()

        return self._deduplicate(apartments)

    def _parse_html(
        self,
        html: str,
        search_url: ImmoweltSearchUrl,
        profile: SearchProfile,
    ) -> list[Apartment]:
        """Parse one result page and map listing cards to Apartment models."""
        soup = BeautifulSoup(html, "html.parser")
        expose_links = self._find_expose_links(soup, search_url.url)
        apartments: list[Apartment] = []

        for link_element, absolute_url in expose_links:
            card = self._find_card_container(link_element)
            card_text = " ".join(card.get_text(" ", strip=True).split()) if card else link_element.get_text(" ", strip=True)
            title = self._extract_title(link_element, card_text)

            if not title or len(card_text) < 20:
                continue

            apartments.append(
                Apartment(
                    source=self.source_name,
                    external_id=stable_id_from_url(absolute_url),
                    title=title,
                    url=absolute_url,
                    city=detect_city(
                        card_text,
                        profile.regions,
                        fallback=search_url.city_hint,
                        language=self.language,
                    ),
                    warm_rent_eur=parse_warm_rent(card_text),
                    rooms=parse_rooms(card_text),
                    living_area_sqm=parse_living_area(card_text),
                    has_kitchen=parse_has_kitchen(card_text),
                    address=None,
                )
            )

        return apartments

    def _find_expose_links(self, soup: BeautifulSoup, base_url: str) -> list[tuple[Any, str]]:
        """Find unique expose detail links on a result page."""
        result: list[tuple[Any, str]] = []
        seen_urls: set[str] = set()

        for link_element in soup.find_all("a", href=True):
            href = str(link_element["href"])
            normalized_href = href.casefold()
            if not any(marker in normalized_href for marker in ("expose", "exposé", "/expose/")):
                continue

            absolute_url = urljoin(base_url, href).split("#", 1)[0]
            if absolute_url in seen_urls:
                continue

            seen_urls.add(absolute_url)
            result.append((link_element, absolute_url))

        return result

    def _find_card_container(self, link_element: Any) -> Any | None:
        """Walk parent nodes to locate the listing card around a link."""
        current = link_element
        for _ in range(8):
            current = current.parent
            if current is None:
                return None
            text = current.get_text(" ", strip=True).casefold()
            has_rent = "€" in text
            has_rooms = "zimmer" in text or " zi" in text
            if has_rent and has_rooms:
                return current
        return link_element.parent

    def _extract_title(self, link_element: Any, card_text: str) -> str:
        """Extract the best available listing title from link or heading text."""
        direct_text = " ".join(link_element.get_text(" ", strip=True).split())
        if len(direct_text) >= 12:
            return direct_text[:180]

        for heading in link_element.find_all(["h1", "h2", "h3", "h4"]):
            heading_text = " ".join(heading.get_text(" ", strip=True).split())
            if len(heading_text) >= 12:
                return heading_text[:180]

        return card_text[:120]

    def _deduplicate(self, apartments: list[Apartment]) -> list[Apartment]:
        """Remove duplicates based on apartment unique key."""
        deduplicated: dict[str, Apartment] = {}
        for apartment in apartments:
            deduplicated[apartment.unique_key] = apartment
        return list(deduplicated.values())

    def _normalize_search_url(self, item: str | dict[str, str]) -> ImmoweltSearchUrl:
        """Normalize URL config items from string or mapping input."""
        if isinstance(item, str):
            return ImmoweltSearchUrl(url=item)
        return ImmoweltSearchUrl(url=item["url"], city_hint=item.get("city_hint"))
