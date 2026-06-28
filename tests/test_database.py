from __future__ import annotations

from datetime import datetime, timedelta, timezone

from apartment_agent.database import ApartmentDatabase
from apartment_agent.models import Apartment, ApartmentMatch


def make_apartment(external_id: str, days_ago: int = 0, city: str = "Boizenburg") -> Apartment:
    found_at = datetime.now(timezone.utc) - timedelta(days=days_ago)
    return Apartment(
        source="demo",
        external_id=external_id,
        title=f"Apartment {external_id}",
        url=f"https://example.com/{external_id}",
        city=city,
        warm_rent_eur=700.0,
        rooms=3.0,
        has_kitchen=True,
        found_at=found_at,
    )


def save_match(database: ApartmentDatabase, apartment: Apartment, rejected: bool, score: int = 80) -> None:
    database.save_match(
        ApartmentMatch(
            apartment=apartment,
            score=score,
            reasons=["test"],
            rejected=rejected,
        )
    )


def test_get_open_apartments_filters_by_rejection_and_last_seen(tmp_path):
    db_path = tmp_path / "test.sqlite3"
    with ApartmentDatabase(db_path) as database:
        recent_open = make_apartment("recent-open", days_ago=1)
        old_open = make_apartment("old-open", days_ago=10)
        recent_rejected = make_apartment("recent-rejected", days_ago=1)

        save_match(database, recent_open, rejected=False, score=90)
        save_match(database, old_open, rejected=False, score=70)
        save_match(database, recent_rejected, rejected=True, score=95)

        open_apartments = database.get_open_apartments(open_days=7)

    assert len(open_apartments) == 1
    assert open_apartments[0]["unique_key"] == recent_open.unique_key


def test_delete_apartment_returns_true_only_for_existing_key(tmp_path):
    db_path = tmp_path / "test.sqlite3"
    apartment = make_apartment("delete-me", days_ago=0)

    with ApartmentDatabase(db_path) as database:
        save_match(database, apartment, rejected=False)

        assert database.delete_apartment(apartment.unique_key) is True
        assert database.delete_apartment(apartment.unique_key) is False


def test_delete_apartments_older_than_days_deletes_only_stale_rows(tmp_path):
    db_path = tmp_path / "test.sqlite3"

    with ApartmentDatabase(db_path) as database:
        old_apartment = make_apartment("old", days_ago=20)
        fresh_apartment = make_apartment("fresh", days_ago=1)
        save_match(database, old_apartment, rejected=False)
        save_match(database, fresh_apartment, rejected=False)

        deleted_count = database.delete_apartments_older_than_days(days=7)
        remaining = database.get_open_apartments(open_days=365)

    assert deleted_count == 1
    assert len(remaining) == 1
    assert remaining[0]["unique_key"] == fresh_apartment.unique_key


def test_get_open_apartments_raises_on_negative_days(tmp_path):
    db_path = tmp_path / "test.sqlite3"

    with ApartmentDatabase(db_path) as database:
        try:
            database.get_open_apartments(open_days=-1)
            raise AssertionError("Expected ValueError")
        except ValueError:
            pass


def test_delete_apartments_older_than_days_raises_on_negative_days(tmp_path):
    db_path = tmp_path / "test.sqlite3"

    with ApartmentDatabase(db_path) as database:
        try:
            database.delete_apartments_older_than_days(days=-1)
            raise AssertionError("Expected ValueError")
        except ValueError:
            pass
