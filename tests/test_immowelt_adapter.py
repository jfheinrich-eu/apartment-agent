"""
Tests for the ImmoweltAdapter.

Verifies that the adapter respects configuration parameters
and behaves correctly with different config combinations.
"""

from bs4 import BeautifulSoup
import pytest
import requests
from unittest.mock import MagicMock, patch

from apartment_agent.models import SearchProfile


def test_immowelt_adapter_respects_config_parameters():
    """
    Verify that ImmoweltAdapter correctly initializes with config parameters.
    """
    from apartment_agent.adapters.immowelt_adapter import ImmoweltAdapter

    search_urls = [
        {
            "url": "https://example.immowelt.de/search",
            "city_hint": "Boizenburg"
        }
    ]
    adapter = ImmoweltAdapter(
        search_urls=search_urls,
        timeout_ms=30_000,
        throttle_seconds=5.0,
    )

    assert adapter.timeout_ms == 30_000
    assert adapter.throttle_seconds == 5.0
    assert len(adapter.search_urls) == 1
    assert adapter.search_urls[0].url == "https://example.immowelt.de/search"
    assert adapter.search_urls[0].city_hint == "Boizenburg"


@pytest.mark.parametrize(
    ("kwargs", "expected_message"),
    [
        ({"timeout_ms": 0}, "timeout_ms must be positive"),
        ({"timeout_ms": "1000"}, "timeout_ms must be a positive number"),
        ({"throttle_seconds": -1}, "throttle_seconds must be non-negative"),
        ({"throttle_seconds": "fast"}, "throttle_seconds must be a non-negative number"),
    ],
)
def test_immowelt_adapter_rejects_invalid_timing_configuration(kwargs, expected_message):
    from apartment_agent.adapters.immowelt_adapter import ImmoweltAdapter

    with pytest.raises(ValueError, match=expected_message):
        ImmoweltAdapter(search_urls=[], **kwargs)


def test_immowelt_adapter_with_empty_urls():
    """
    Verify that ImmoweltAdapter gracefully handles empty search_urls list.
    """
    from apartment_agent.adapters.immowelt_adapter import ImmoweltAdapter

    adapter = ImmoweltAdapter(search_urls=[])
    profile = SearchProfile(
        max_warm_rent=800,
        min_rooms=2.5,
        kitchen_required=True,
        regions=["Boizenburg"],
    )

    # Should return empty list if no URLs configured
    result = adapter.search(profile)
    assert result == []


def test_immowelt_adapter_normalizes_search_urls():
    """
    Verify that ImmoweltAdapter normalizes search URLs from different formats.
    """
    from apartment_agent.adapters.immowelt_adapter import ImmoweltAdapter

    search_urls = [
        "https://example.immowelt.de/search1",  # string format
        {  # dict format
            "url": "https://example.immowelt.de/search2",
            "city_hint": "Lüneburg"
        }
    ]
    adapter = ImmoweltAdapter(search_urls=search_urls)

    assert len(adapter.search_urls) == 2
    assert adapter.search_urls[0].url == "https://example.immowelt.de/search1"
    assert adapter.search_urls[0].city_hint is None
    assert adapter.search_urls[1].url == "https://example.immowelt.de/search2"
    assert adapter.search_urls[1].city_hint == "Lüneburg"


def test_immowelt_adapter_has_source_name():
    """
    Verify that ImmoweltAdapter has correct source name.
    """
    from apartment_agent.adapters.immowelt_adapter import ImmoweltAdapter

    adapter = ImmoweltAdapter(search_urls=[])
    assert adapter.source_name == "immowelt"


def test_find_expose_links_and_deduplicate():
    from apartment_agent.adapters.immowelt_adapter import ImmoweltAdapter

    adapter = ImmoweltAdapter(search_urls=[])
    soup = BeautifulSoup(
        '<a href="/expose/123">One</a><a href="/expose/123#foo">Dup</a><a href="/other">Skip</a>',
        "html.parser",
    )

    links = adapter._find_expose_links(soup, "https://example.immowelt.de")
    assert len(links) == 1
    assert links[0][1].endswith("/expose/123")


def test_extract_title_and_card_container_helpers():
    from apartment_agent.adapters.immowelt_adapter import ImmoweltAdapter

    adapter = ImmoweltAdapter(search_urls=[])
    soup = BeautifulSoup(
        '<div><article><h2>Sehr schoene Wohnung mit Balkon</h2><a href="/expose/1">Details</a> 750 € 3 Zimmer</article></div>',
        "html.parser",
    )
    link = soup.find("a")
    assert link is not None

    card = adapter._find_card_container(link)
    assert card is not None

    title = adapter._extract_title(link, "Fallback card text")
    assert isinstance(title, str)
    assert len(title) > 0


def test_parse_html_extracts_apartment():
    from apartment_agent.adapters.immowelt_adapter import ImmoweltAdapter, ImmoweltSearchUrl

    adapter = ImmoweltAdapter(search_urls=[], language="en")
    profile = SearchProfile(
        max_warm_rent=800,
        min_rooms=2.5,
        kitchen_required=True,
        regions=["Boizenburg"],
    )

    html = (
        '<article><a href="/expose/987654">'
        '<h2>Apartment title with balcony</h2>'
        'Boizenburg 750 € 3 Zimmer 68 m² Einbauküche'
        "</a></article>"
    )

    result = adapter._parse_html(
        html,
        ImmoweltSearchUrl(url="https://example.immowelt.de/search", city_hint="Boizenburg"),
        profile,
    )
    assert len(result) == 1
    assert result[0].city == "Boizenburg"
    assert result[0].rooms == 3


def test_search_handles_request_exception_without_crash():
    from apartment_agent.adapters.immowelt_adapter import ImmoweltAdapter

    adapter = ImmoweltAdapter(search_urls=["https://example.immowelt.de/search"])
    profile = SearchProfile(
        max_warm_rent=800,
        min_rooms=2.5,
        kitchen_required=True,
        regions=["Boizenburg"],
    )

    session_instance = MagicMock()
    session_instance.get.side_effect = requests.RequestException("boom")

    with patch("apartment_agent.adapters.immowelt_adapter.requests.Session", return_value=session_instance):
        result = adapter.search(profile)
    assert result == []


def test_extract_title_uses_card_fallback_when_link_text_short():
    from apartment_agent.adapters.immowelt_adapter import ImmoweltAdapter

    adapter = ImmoweltAdapter(search_urls=[])
    soup = BeautifulSoup('<a href="/expose/1">Mehr</a>', "html.parser")
    link = soup.find("a")
    assert link is not None

    title = adapter._extract_title(link, "Card fallback title text")
    assert title.startswith("Card fallback")
