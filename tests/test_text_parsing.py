from apartment_agent.adapters.text_parsing import (
    detect_city,
    stable_id_from_url,
    parse_has_kitchen,
    parse_living_area,
    parse_rooms,
    parse_warm_rent,
)


def test_parse_warm_rent():
    assert parse_warm_rent("Warmmiete 760 €") == 760
    assert parse_warm_rent("760,50 € warm") == 760.5


def test_parse_rooms():
    assert parse_rooms("2,5 Zimmer") == 2.5
    assert parse_rooms("3 Zi.") == 3


def test_parse_living_area():
    assert parse_living_area("68 m²") == 68


def test_parse_has_kitchen():
    assert parse_has_kitchen("mit Einbauküche") is True
    assert parse_has_kitchen("keine Einbauküche") is False
    assert parse_has_kitchen("schöne Wohnung") is None


def test_stable_id_from_url_fallback_hash():
    # No numeric / expose-like pattern in path or query -> hash fallback
    assert len(stable_id_from_url("https://example.com/listing/no-id-here")) == 16


def test_detect_city_with_fallback_and_language():
    assert detect_city("foo", ["Boizenburg"], fallback="Lüneburg", language="de") == "Lüneburg"
    assert detect_city("foo", ["Boizenburg"], language="de") == "Unbekannt"
    assert detect_city("foo", ["Boizenburg"], language="en") == "Unknown"
