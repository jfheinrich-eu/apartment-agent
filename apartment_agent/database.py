from __future__ import annotations

import sqlite3
from datetime import datetime, timedelta, timezone
from pathlib import Path
from apartment_agent.models import Apartment, ApartmentMatch


class ApartmentDatabase:
    """Persist apartment matches in SQLite."""

    def __init__(self, database_path: str | Path = "apartments.sqlite3") -> None:
        """Open a database connection and initialize the schema."""
        self.database_path = Path(database_path).resolve()
        self.connection = sqlite3.connect(self.database_path)
        self.connection.row_factory = sqlite3.Row
        self._create_schema()

    def _create_schema(self) -> None:
        """Create the apartments table if it does not exist yet."""
        self.connection.execute(
            """
            CREATE TABLE IF NOT EXISTS apartments (
                unique_key TEXT PRIMARY KEY,
                source TEXT NOT NULL,
                external_id TEXT NOT NULL,
                title TEXT NOT NULL,
                url TEXT NOT NULL,
                city TEXT NOT NULL,
                warm_rent_eur REAL,
                rooms REAL,
                living_area_sqm REAL,
                has_kitchen INTEGER,
                address TEXT,
                internet_status TEXT NOT NULL,
                found_at TEXT NOT NULL,
                last_seen_at TEXT NOT NULL,
                score INTEGER,
                rejected INTEGER NOT NULL
            )
            """
        )
        self.connection.commit()

    def exists(self, apartment: Apartment) -> bool:
        """Return True when an apartment with the same unique key already exists."""
        cursor = self.connection.execute(
            "SELECT 1 FROM apartments WHERE unique_key = ?",
            (apartment.unique_key,),
        )
        return cursor.fetchone() is not None

    def save_match(self, apartment_match: ApartmentMatch) -> bool:
        """Insert or update a scored apartment match and return whether it was new."""
        apartment = apartment_match.apartment
        is_new = not self.exists(apartment)

        self.connection.execute(
            """
            INSERT INTO apartments (
                unique_key, source, external_id, title, url, city, warm_rent_eur,
                rooms, living_area_sqm, has_kitchen, address, internet_status,
                found_at, last_seen_at, score, rejected
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(unique_key) DO UPDATE SET
                last_seen_at = excluded.last_seen_at,
                score = excluded.score,
                rejected = excluded.rejected
            """,
            (
                apartment.unique_key,
                apartment.source,
                apartment.external_id,
                apartment.title,
                str(apartment.url),
                apartment.city,
                apartment.warm_rent_eur,
                apartment.rooms,
                apartment.living_area_sqm,
                None if apartment.has_kitchen is None else int(apartment.has_kitchen),
                apartment.address,
                apartment.internet_status.value,
                apartment.found_at.isoformat(),
                apartment.found_at.isoformat(),
                apartment_match.score,
                int(apartment_match.rejected),
            ),
        )
        self.connection.commit()
        return is_new

    def get_open_apartments(self, open_days: int = 7) -> list[dict[str, object]]:
        """Return non-rejected apartments seen within the last open_days days."""
        if open_days < 0:
            raise ValueError("open_days must be >= 0")

        cutoff = datetime.now(timezone.utc) - timedelta(days=open_days)
        cursor = self.connection.execute(
            """
            SELECT * FROM apartments
            WHERE rejected = 0 AND last_seen_at >= ?
            ORDER BY COALESCE(score, -1) DESC, last_seen_at DESC
            """,
            (cutoff.isoformat(),),
        )
        return [dict(row) for row in cursor.fetchall()]

    def delete_apartment(self, unique_key: str) -> bool:
        """Delete one apartment by unique key and return True when it existed."""
        cursor = self.connection.execute(
            "DELETE FROM apartments WHERE unique_key = ?",
            (unique_key,),
        )
        self.connection.commit()
        return cursor.rowcount > 0

    def delete_apartments_older_than_days(self, days: int) -> int:
        """Delete apartments with last_seen_at older than the given number of days."""
        if days < 0:
            raise ValueError("days must be >= 0")

        cutoff = datetime.now(timezone.utc) - timedelta(days=days)
        cursor = self.connection.execute(
            "DELETE FROM apartments WHERE last_seen_at < ?",
            (cutoff.isoformat(),),
        )
        self.connection.commit()
        return cursor.rowcount

    def close(self) -> None:
        """Close the SQLite connection."""
        self.connection.close()

    def __enter__(self) -> ApartmentDatabase:
        """Return the database instance for use in a context manager."""
        return self

    def __exit__(self, exc_type, exc_value, exc_traceback) -> None:
        """Close the database connection when leaving a context manager."""
        self.close()
