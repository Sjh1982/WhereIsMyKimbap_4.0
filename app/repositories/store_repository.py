from __future__ import annotations

from math import asin, cos, radians, sin, sqrt

import duckdb

from app.database import Database
from app.exceptions import DatabaseOperationError
from app.models import Store


def haversine_meters(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    earth_radius = 6_371_000
    dlat = radians(lat2 - lat1)
    dlon = radians(lon2 - lon1)
    a = sin(dlat / 2) ** 2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlon / 2) ** 2
    return 2 * earth_radius * asin(sqrt(a))


class StoreRepository:
    def __init__(self, database: Database) -> None:
        self.database = database

    def find_nearby(self, latitude: float, longitude: float, radius_meters: float = 2_000) -> list[Store]:
        try:
            with self.database.connection() as connection:
                rows = connection.execute(
                    """SELECT store_id, store_name, brand, address, latitude, longitude,
                              opening_hours, image_path, is_active
                       FROM stores WHERE is_active = TRUE"""
                ).fetchall()
            stores = [
                Store(*row, haversine_meters(latitude, longitude, row[4], row[5]))
                for row in rows
            ]
            return sorted(
                (store for store in stores if store.distance_meters <= radius_meters),
                key=lambda store: store.distance_meters,
            )
        except duckdb.Error as exc:
            print(f"[DuckDB] 주변 매장 조회 실패: {exc}")
            raise DatabaseOperationError("주변 편의점을 불러오지 못했습니다.") from exc

    def find_all(self, include_inactive: bool = False) -> list[Store]:
        condition = "" if include_inactive else "WHERE is_active = TRUE"
        with self.database.connection() as connection:
            rows = connection.execute(
                f"""SELECT store_id, store_name, brand, address, latitude, longitude,
                            opening_hours, image_path, is_active FROM stores {condition}
                     ORDER BY store_name"""
            ).fetchall()
        return [Store(*row) for row in rows]
