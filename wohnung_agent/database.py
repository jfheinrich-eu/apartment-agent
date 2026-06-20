from __future__ import annotations

import sqlite3
from pathlib import Path
from wohnung_agent.models import Apartment, ApartmentMatch


class ApartmentDatabase:
    def __init__(self, database_path: str | Path = "wohnungen.sqlite3") -> None:
        self.database_path = Path(database_path).resolve()
        self.connection = sqlite3.connect(self.database_path)
        self.connection.row_factory = sqlite3.Row
        self._create_schema()

    def _create_schema(self) -> None:
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
        cursor = self.connection.execute(
            "SELECT 1 FROM apartments WHERE unique_key = ?",
            (apartment.unique_key,),
        )
        return cursor.fetchone() is not None

    def save_match(self, apartment_match: ApartmentMatch) -> bool:
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

    def close(self) -> None:
        self.connection.close()
