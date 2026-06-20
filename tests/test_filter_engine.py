from wohnung_agent.filter_engine import FilterEngine
from wohnung_agent.models import Apartment, InternetStatus, SearchProfile


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
    assert any("City matches" in reason for reason in result.reasons)
    assert any("Warm rent" in reason for reason in result.reasons)


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


def test_filter_engine_german_language_and_negative_paths():
    profile = SearchProfile(
        max_warm_rent=700,
        min_rooms=3.0,
        kitchen_required=True,
        regions=["Boizenburg"],
    )
    apartment = Apartment(
        source="test",
        external_id="3",
        title="Ohne passende Werte",
        url="https://example.com/3",
        city="Hamburg",
        warm_rent_eur=950,
        rooms=2.0,
        has_kitchen=False,
        internet_status=InternetStatus.NOT_AVAILABLE_1000,
    )

    result = FilterEngine(profile, language="de").evaluate(apartment)

    assert result.rejected is True
    assert any("Ort passt nicht" in reason for reason in result.reasons)
    assert any("Warmmiete zu hoch" in reason for reason in result.reasons)
    assert any("Zu wenige Zimmer" in reason for reason in result.reasons)
    assert any("Keine Einbaukueche" in reason for reason in result.reasons)
    assert any("nicht verfuegbar" in reason for reason in result.reasons)


def test_filter_engine_missing_optional_values_branch():
    profile = SearchProfile(
        max_warm_rent=800,
        min_rooms=2.5,
        kitchen_required=True,
        regions=["Boizenburg"],
    )
    apartment = Apartment(
        source="test",
        external_id="4",
        title="Unknown values",
        url="https://example.com/4",
        city="Boizenburg",
        warm_rent_eur=None,
        rooms=None,
        has_kitchen=None,
        address="Teststrasse 1",
        internet_status=InternetStatus.AVAILABLE_1000,
    )

    result = FilterEngine(profile, language="en").evaluate(apartment)

    assert result.rejected is False
    assert any("Warm rent missing" in reason for reason in result.reasons)
    assert any("Room count missing" in reason for reason in result.reasons)
    assert any("Built-in kitchen unclear" in reason for reason in result.reasons)
    assert any("Address available" in reason for reason in result.reasons)
    assert any("Vodafone Cable 1000 available" in reason for reason in result.reasons)
