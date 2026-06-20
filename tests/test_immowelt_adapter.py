"""
Tests for the ImmoweltAdapter.

Verifies that the adapter respects configuration parameters
and behaves correctly with different config combinations.
"""

from wohnung_agent.models import SearchProfile


def test_immowelt_adapter_respects_config_parameters():
    """
    Verify that ImmoweltAdapter correctly initializes with config parameters.
    """
    from wohnung_agent.adapters.immowelt_adapter import ImmoweltAdapter

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


def test_immowelt_adapter_with_empty_urls():
    """
    Verify that ImmoweltAdapter gracefully handles empty search_urls list.
    """
    from wohnung_agent.adapters.immowelt_adapter import ImmoweltAdapter

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
    from wohnung_agent.adapters.immowelt_adapter import ImmoweltAdapter

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
    from wohnung_agent.adapters.immowelt_adapter import ImmoweltAdapter

    adapter = ImmoweltAdapter(search_urls=[])
    assert adapter.source_name == "immowelt"
