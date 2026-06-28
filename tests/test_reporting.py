from wohnung_agent.reporting import generate_open_apartments_markdown


def test_generate_open_apartments_markdown_contains_table_and_values():
    apartments = [
        {
            "unique_key": "immowelt:123",
            "city": "Boizenburg",
            "title": "Nice apartment",
            "warm_rent_eur": 750.0,
            "rooms": 3.0,
            "score": 88,
            "found_at": "2026-06-19T10:00:00+00:00",
            "last_seen_at": "2026-06-20T10:00:00+00:00",
            "url": "https://example.com/123",
        }
    ]

    report = generate_open_apartments_markdown(apartments=apartments, open_days=7, language="en")

    assert "# Open apartments report" in report
    assert "| Unique key | City | Title | Rent (EUR) | Rooms | Score | Found at | Last seen at | URL |" in report
    assert "immowelt:123" in report
    assert "Nice apartment" in report
    assert "750.0" in report


def test_generate_open_apartments_markdown_handles_empty_result_set():
    report = generate_open_apartments_markdown(apartments=[], open_days=7, language="en")

    assert "No open apartments found." in report
    assert "Apartments: 0" in report
