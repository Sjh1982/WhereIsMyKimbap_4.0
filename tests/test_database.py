from __future__ import annotations

import duckdb
import pytest


TABLES = {
    "users", "stores", "categories", "products", "inventories",
    "carts", "cart_items", "orders", "order_items", "payments",
}


def test_schema_and_seed_counts(database):
    with database.connection() as connection:
        assert {row[0] for row in connection.execute("SHOW TABLES").fetchall()} == TABLES
        assert connection.execute("SELECT count(*) FROM products").fetchone()[0] == 100
        assert connection.execute("SELECT count(*) FROM stores").fetchone()[0] == 5
        assert connection.execute("SELECT count(*) FROM inventories").fetchone()[0] == 316


def test_seed_is_idempotent(database):
    with database.connection() as connection:
        before = connection.execute("SELECT count(*) FROM products").fetchone()[0]
    database.initialize(seed=True)
    with database.connection() as connection:
        after = connection.execute("SELECT count(*) FROM products").fetchone()[0]
    assert before == after == 100


def test_constraints_block_negative_and_empty_values(database):
    with database.connection() as connection:
        with pytest.raises(duckdb.ConstraintException):
            connection.execute(
                "UPDATE inventories SET selling_price=-1 WHERE store_id=1 AND product_id=1"
            )
        with pytest.raises(duckdb.ConstraintException):
            connection.execute(
                """INSERT INTO categories VALUES (99, '   ', 99)"""
            )


def test_image_paths_are_relative(database):
    with database.connection() as connection:
        paths = [row[0] for row in connection.execute(
            "SELECT image_path FROM products UNION ALL SELECT image_path FROM stores"
        ).fetchall()]
    assert paths
    assert all(not path.startswith(("/", "\\")) and ":" not in path for path in paths)
