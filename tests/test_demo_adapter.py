from wohnung_agent.adapters.demo_adapter import DemoAdapter
from wohnung_agent.models import Apartment, SearchProfile


def test_demo_adapter_search_returns_apartments():
    """Verify that DemoAdapter.search() returns a list of Apartment objects."""
    profile = SearchProfile(
        max_warm_rent=800,
        min_rooms=2.5,
        kitchen_required=True,
        regions=["Boizenburg", "Lüneburg"],
    )

    adapter = DemoAdapter()
    apartments = adapter.search(profile)

    assert isinstance(apartments, list)
    assert len(apartments) > 0
    assert all(isinstance(apt, Apartment) for apt in apartments)


def test_demo_adapter_apartments_have_required_fields():
    """Verify that DemoAdapter returns apartments with required fields."""
    profile = SearchProfile(
        max_warm_rent=800,
        min_rooms=2.5,
        kitchen_required=True,
        regions=["Boizenburg", "Lüneburg"],
    )

    adapter = DemoAdapter()
    apartments = adapter.search(profile)

    for apartment in apartments:
        assert apartment.source is not None
        assert apartment.external_id is not None
        assert apartment.title is not None
        assert apartment.url is not None
        assert apartment.city is not None


def test_demo_adapter_has_source_name():
    """Verify that DemoAdapter has source_name attribute."""
    adapter = DemoAdapter()
    assert hasattr(adapter, "source_name")
    assert adapter.source_name == "demo"
