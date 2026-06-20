from wohnung_agent.adapters.text_parsing import (
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
