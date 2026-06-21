from __future__ import annotations

import duckdb

from app.database import Database
from app.exceptions import DatabaseOperationError, NotFoundError, ValidationError
from app.models import ProductStock


PRODUCT_STOCK_COLUMNS = (
    "product_id", "product_name", "category_name", "manufacturer", "package_size",
    "image_path", "store_id", "store_name", "selling_price", "stock_count",
    "shelf_location", "updated_at",
)


class ProductRepository:
    def __init__(self, database: Database) -> None:
        self.database = database

    @staticmethod
    def _map(row: tuple) -> ProductStock:
        return ProductStock(**dict(zip(PRODUCT_STOCK_COLUMNS, row)))

    def find_by_store(self, store_id: int, keyword: str = "", category_id: int | None = None) -> list[ProductStock]:
        sql = """SELECT p.product_id, p.product_name, c.category_name, p.manufacturer,
                        p.package_size, p.image_path, s.store_id, s.store_name,
                        i.selling_price, i.stock_count, i.shelf_location, i.updated_at
                 FROM stores s
                 JOIN inventories i ON i.store_id = s.store_id
                 JOIN products p ON p.product_id = i.product_id
                 JOIN categories c ON c.category_id = p.category_id
                 WHERE s.store_id = ? AND lower(p.product_name) LIKE lower(?)"""
        params: list[object] = [store_id, f"%{keyword.strip()}%"]
        if category_id is not None:
            sql += " AND c.category_id = ?"
            params.append(category_id)
        sql += " ORDER BY c.display_order, p.product_name"
        try:
            with self.database.connection() as connection:
                return [self._map(row) for row in connection.execute(sql, params).fetchall()]
        except duckdb.Error as exc:
            print(f"[DuckDB] 매장 상품 조회 실패: {exc}")
            raise DatabaseOperationError("매장 상품과 재고를 불러오지 못했습니다.") from exc

    def compare_by_product(self, keyword: str = "") -> list[ProductStock]:
        sql = """SELECT p.product_id, p.product_name, c.category_name, p.manufacturer,
                        p.package_size, p.image_path, s.store_id, s.store_name,
                        i.selling_price, i.stock_count, i.shelf_location, i.updated_at
                 FROM products p
                 JOIN categories c ON c.category_id = p.category_id
                 LEFT JOIN inventories i ON i.product_id = p.product_id
                 LEFT JOIN stores s ON s.store_id = i.store_id
                 WHERE lower(p.product_name) LIKE lower(?)
                 ORDER BY p.product_name, i.selling_price NULLS LAST, s.store_name"""
        with self.database.connection() as connection:
            return [self._map(row) for row in connection.execute(sql, [f"%{keyword.strip()}%"]).fetchall()]

    def categories(self) -> list[tuple[int, str]]:
        with self.database.connection() as connection:
            return connection.execute(
                "SELECT category_id, category_name FROM categories ORDER BY display_order"
            ).fetchall()

    def update_inventory(self, store_id: int, product_id: int, price: int, stock: int, shelf: str) -> None:
        if price < 0 or stock < 0 or not shelf.strip():
            raise ValueError("가격·재고는 음수가 아니어야 하며 진열 위치는 필수입니다.")
        with self.database.connection() as connection:
            result = connection.execute(
                """UPDATE inventories SET selling_price=?, stock_count=?, shelf_location=?, updated_at=current_timestamp
                   WHERE store_id=? AND product_id=? RETURNING store_id""",
                [price, stock, shelf.strip(), store_id, product_id],
            ).fetchone()
        if result is None:
            raise NotFoundError("수정할 매장 상품 재고가 없습니다.")

    def create_product(self, category_id: int, name: str, manufacturer: str, package_size: str,
                       image_path: str = "assets/images/default_product.png") -> int:
        values = [name.strip(), manufacturer.strip(), package_size.strip()]
        if any(not value for value in values):
            raise ValidationError("상품명, 제조사, 포장 단위는 필수입니다.")
        if image_path.startswith(("/", "\\")) or ":" in image_path:
            raise ValidationError("이미지는 프로젝트 내부 상대경로만 사용할 수 있습니다.")
        try:
            with self.database.connection() as connection:
                product_id = connection.execute("SELECT coalesce(max(product_id), 0) + 1 FROM products").fetchone()[0]
                connection.execute(
                    """INSERT INTO products VALUES (?, ?, ?, ?, ?, '관리 화면에서 추가한 상품', ?, FALSE)""",
                    [product_id, category_id, *values, image_path],
                )
            return product_id
        except duckdb.ConstraintException as exc:
            raise ValidationError("이미 등록된 상품이거나 카테고리가 올바르지 않습니다.") from exc

    def delete_product(self, product_id: int) -> None:
        try:
            with self.database.connection() as connection:
                result = connection.execute(
                    "DELETE FROM products WHERE product_id=? RETURNING product_id", [product_id]
                ).fetchone()
            if result is None:
                raise NotFoundError("삭제할 상품을 찾지 못했습니다.")
        except duckdb.ConstraintException as exc:
            raise ValidationError("재고·장바구니·주문 내역이 연결된 상품은 삭제할 수 없습니다.") from exc

    def upsert_inventory(self, store_id: int, product_id: int, price: int, stock: int, shelf: str) -> None:
        if price < 0 or stock < 0 or not shelf.strip():
            raise ValidationError("가격·재고는 음수가 아니어야 하며 진열 위치는 필수입니다.")
        try:
            with self.database.connection() as connection:
                connection.execute(
                    """INSERT INTO inventories VALUES (?, ?, ?, ?, ?, current_timestamp)
                       ON CONFLICT (store_id, product_id) DO UPDATE SET
                       selling_price=excluded.selling_price, stock_count=excluded.stock_count,
                       shelf_location=excluded.shelf_location, updated_at=excluded.updated_at""",
                    [store_id, product_id, price, stock, shelf.strip()],
                )
        except duckdb.Error as exc:
            raise DatabaseOperationError("재고를 저장하지 못했습니다. 매장과 상품을 확인하세요.") from exc

    def delete_inventory(self, store_id: int, product_id: int) -> None:
        with self.database.connection() as connection:
            result = connection.execute(
                "DELETE FROM inventories WHERE store_id=? AND product_id=? RETURNING store_id",
                [store_id, product_id],
            ).fetchone()
        if result is None:
            raise NotFoundError("삭제할 재고 관계를 찾지 못했습니다.")
