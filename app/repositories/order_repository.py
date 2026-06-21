from __future__ import annotations

import uuid
from datetime import datetime

from app.database import Database
from app.exceptions import InsufficientStockError, NotFoundError
from app.models import OrderSummary


class OrderRepository:
    def __init__(self, database: Database) -> None:
        self.database = database

    def place_from_cart(self, user_id: int, payment_method: str) -> int:
        with self.database.transaction() as connection:
            lines = connection.execute(
                """SELECT c.cart_id, c.store_id, ci.product_id, ci.quantity,
                          i.selling_price, i.stock_count, p.product_name
                   FROM carts c JOIN cart_items ci ON ci.cart_id=c.cart_id
                   JOIN products p ON p.product_id=ci.product_id
                   JOIN inventories i ON i.store_id=c.store_id AND i.product_id=ci.product_id
                   WHERE c.user_id=?""", [user_id]
            ).fetchall()
            if not lines:
                raise NotFoundError("장바구니가 비어 있어 주문할 수 없습니다.")
            for line in lines:
                if line[3] > line[5]:
                    raise InsufficientStockError(f"{line[6]} 재고가 부족합니다. 현재 {line[5]}개")
            order_id = connection.execute("SELECT coalesce(max(order_id), 0) + 1 FROM orders").fetchone()[0]
            payment_id = connection.execute("SELECT coalesce(max(payment_id), 0) + 1 FROM payments").fetchone()[0]
            total = sum(line[3] * line[4] for line in lines)
            barcode = uuid.uuid4().hex[:8].upper()
            now = datetime.now()
            connection.execute(
                "INSERT INTO orders VALUES (?, ?, ?, ?, 'PENDING', ?, ?, NULL, NULL)",
                [order_id, user_id, lines[0][1], barcode, total, now],
            )
            for _, store_id, product_id, quantity, price, _, _ in lines:
                connection.execute("INSERT INTO order_items VALUES (?, ?, ?, ?)", [order_id, product_id, quantity, price])
                connection.execute(
                    "UPDATE inventories SET stock_count=stock_count-?, updated_at=current_timestamp WHERE store_id=? AND product_id=?",
                    [quantity, store_id, product_id],
                )
            connection.execute(
                "INSERT INTO payments VALUES (?, ?, ?, ?, 'PAID', ?, NULL)",
                [payment_id, order_id, total, payment_method, now],
            )
            connection.execute("DELETE FROM cart_items WHERE cart_id=?", [lines[0][0]])
            connection.execute("UPDATE carts SET updated_at=? WHERE cart_id=?", [now, lines[0][0]])
            return order_id

    def find_by_user(self, user_id: int) -> list[OrderSummary]:
        with self.database.connection() as connection:
            rows = connection.execute(
                """SELECT o.order_id, s.store_name, o.pickup_barcode, o.status, o.total_amount,
                          p.payment_method, p.status, o.created_at
                   FROM orders o JOIN stores s ON s.store_id=o.store_id
                   JOIN payments p ON p.order_id=o.order_id
                   WHERE o.user_id=? ORDER BY o.created_at DESC""", [user_id]
            ).fetchall()
        return [OrderSummary(*row) for row in rows]

    def pickup(self, order_id: int, user_id: int) -> None:
        with self.database.connection() as connection:
            row = connection.execute(
                "UPDATE orders SET status='PICKED_UP', picked_up_at=current_timestamp WHERE order_id=? AND user_id=? AND status='PENDING' RETURNING order_id",
                [order_id, user_id],
            ).fetchone()
        if row is None:
            raise NotFoundError("수령 가능한 주문을 찾지 못했습니다.")
