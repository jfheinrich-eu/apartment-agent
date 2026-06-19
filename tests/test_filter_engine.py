from wohnung_agent.filter_engine import FilterEngine
from wohnung_agent.models import Apartment, SearchProfile


def test_matching_apartment_is_not_rejected():
    profile = SearchProfile(
        max_warm_rent=800,
        min_rooms=2.5,
        kitchen_required=True,
        regions=["Boizenburg"],
    )
    apartment = Apartment(
        source="test",
        external_id="1",
        title="Testwohnung",
        url="https://example.com/1",
        city="Boizenburg",
        warm_rent_eur=750,
        rooms=2.5,
        has_kitchen=True,
    )

    result = FilterEngine(profile).evaluate(apartment)

    assert result.rejected is False
    assert result.score >= 80


def test_expensive_apartment_is_rejected():
    profile = SearchProfile(
        max_warm_rent=800,
        min_rooms=2.5,
        kitchen_required=True,
        regions=["Lüneburg"],
    )
    apartment = Apartment(
        source="test",
        external_id="2",
        title="Teure Wohnung",
        url="https://example.com/2",
        city="Lüneburg",
        warm_rent_eur=950,
        rooms=3,
        has_kitchen=True,
    )

    result = FilterEngine(profile).evaluate(apartment)

    assert result.rejected is True
