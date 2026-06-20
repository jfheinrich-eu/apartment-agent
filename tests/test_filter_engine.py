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


def test_result_has_reasons():
    """Verify that evaluate() returns ApartmentMatch with reasons list."""
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

    assert hasattr(result, "reasons")
    assert isinstance(result.reasons, list)
    assert len(result.reasons) > 0
    assert any("Ort passt" in reason for reason in result.reasons)
    assert any("Warmmiete" in reason for reason in result.reasons)


def test_result_is_apartment_match():
    """Verify that evaluate() returns an ApartmentMatch object with correct fields."""
    from wohnung_agent.models import ApartmentMatch

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

    assert isinstance(result, ApartmentMatch)
    assert result.apartment == apartment
    assert isinstance(result.score, int)
    assert isinstance(result.rejected, bool)
    assert isinstance(result.reasons, list)
