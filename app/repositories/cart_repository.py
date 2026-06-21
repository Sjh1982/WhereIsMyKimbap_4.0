from __future__ import annotations

from datetime import datetime

from app.database import Database
from app.exceptions import InsufficientStockError, NotFoundError, ValidationError
from app.models import CartLine


class CartRepository:
    def __init__(self, database: Database) -> None:
        self.database = database

    def get_lines(self, user_id: int) -> list[CartLine]:
        with self.database.connection() as connection:
            rows = connection.execute(
                """SELECT c.cart_id, c.store_id, s.store_name, p.product_id, p.product_name,
                          i.selling_price, ci.quantity, i.stock_count
                   FROM carts c
                   JOIN stores s ON s.store_id = c.store_id
                   JOIN cart_items ci ON ci.cart_id = c.cart_id
                   JOIN products p ON p.product_id = ci.product_id
                   JOIN inventories i ON i.store_id = c.store_id AND i.product_id = ci.product_id
                   WHERE c.user_id = ? ORDER BY ci.added_at""",
                [user_id],
            ).fetchall()
        return [CartLine(*row) for row in rows]

    def add_item(self, user_id: int, store_id: int, product_id: int, quantity: int = 1) -> None:
        if quantity <= 0:
            raise ValidationError("장바구니 수량은 1개 이상이어야 합니다.")
        with self.database.transaction() as connection:
            inventory = connection.execute(
                "SELECT stock_count FROM inventories WHERE store_id=? AND product_id=?",
                [store_id, product_id],
            ).fetchone()
            if inventory is None:
                raise NotFoundError("선택한 매장에서 해당 상품을 판매하지 않습니다.")
            cart = connection.execute("SELECT cart_id, store_id FROM carts WHERE user_id=?", [user_id]).fetchone()
            if cart and cart[1] != store_id:
                item_count = connection.execute(
                    "SELECT count(*) FROM cart_items WHERE cart_id=?", [cart[0]]
                ).fetchone()[0]
                if item_count:
                    raise ValidationError("한 장바구니에는 한 매장의 상품만 담을 수 있습니다. 기존 장바구니를 비워주세요.")
                connection.execute(
                    "UPDATE carts SET store_id=?, updated_at=? WHERE cart_id=?",
                    [store_id, datetime.now(), cart[0]],
                )
                cart = (cart[0], store_id)
            if cart is None:
                cart_id = connection.execute("SELECT coalesce(max(cart_id), 0) + 1 FROM carts").fetchone()[0]
                now = datetime.now()
                connection.execute("INSERT INTO carts VALUES (?, ?, ?, ?, ?)", [cart_id, user_id, store_id, now, now])
            else:
                cart_id = cart[0]
            current = connection.execute(
                "SELECT quantity FROM cart_items WHERE cart_id=? AND product_id=?", [cart_id, product_id]
            ).fetchone()
            desired = quantity + (current[0] if current else 0)
            if desired > inventory[0]:
                raise InsufficientStockError(f"현재 재고는 {inventory[0]}개입니다.")
            connection.execute(
                """INSERT INTO cart_items VALUES (?, ?, ?, ?)
                   ON CONFLICT (cart_id, product_id) DO UPDATE
                   SET quantity=excluded.quantity, added_at=excluded.added_at""",
                [cart_id, product_id, desired, datetime.now()],
            )

    def update_quantity(self, user_id: int, product_id: int, quantity: int) -> None:
        if quantity <= 0:
            self.remove_item(user_id, product_id)
            return
        with self.database.connection() as connection:
            row = connection.execute(
                """SELECT c.cart_id, i.stock_count FROM carts c
                   JOIN inventories i ON i.store_id=c.store_id AND i.product_id=?
                   WHERE c.user_id=?""", [product_id, user_id]
            ).fetchone()
            if row is None:
                raise NotFoundError("장바구니 상품을 찾지 못했습니다.")
            if quantity > row[1]:
                raise InsufficientStockError(f"현재 재고는 {row[1]}개입니다.")
            connection.execute("UPDATE cart_items SET quantity=? WHERE cart_id=? AND product_id=?", [quantity, row[0], product_id])

    def remove_item(self, user_id: int, product_id: int) -> None:
        with self.database.transaction() as connection:
            cart = connection.execute("SELECT cart_id FROM carts WHERE user_id=?", [user_id]).fetchone()
            if cart is None:
                return
            connection.execute("DELETE FROM cart_items WHERE cart_id=? AND product_id=?", [cart[0], product_id])

    def clear(self, user_id: int) -> None:
        with self.database.transaction() as connection:
            cart = connection.execute("SELECT cart_id FROM carts WHERE user_id=?", [user_id]).fetchone()
            if cart:
                connection.execute("DELETE FROM cart_items WHERE cart_id=?", [cart[0]])
