from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True, slots=True)
class Store:
    store_id: int
    store_name: str
    brand: str
    address: str
    latitude: float
    longitude: float
    opening_hours: str | None
    image_path: str
    is_active: bool
    distance_meters: float | None = None


@dataclass(frozen=True, slots=True)
class ProductStock:
    product_id: int
    product_name: str
    category_name: str
    manufacturer: str
    package_size: str
    image_path: str
    store_id: int | None
    store_name: str | None
    selling_price: int | None
    stock_count: int | None
    shelf_location: str | None
    updated_at: datetime | None

    @property
    def stock_status(self) -> str:
        if self.stock_count is None:
            return "재고 미등록"
        if self.stock_count == 0:
            return "품절"
        if self.stock_count <= 2:
            return "재고 부족"
        return "재고 있음"


@dataclass(frozen=True, slots=True)
class CartLine:
    cart_id: int
    store_id: int
    store_name: str
    product_id: int
    product_name: str
    selling_price: int
    quantity: int
    stock_count: int

    @property
    def line_total(self) -> int:
        return self.selling_price * self.quantity


@dataclass(frozen=True, slots=True)
class OrderSummary:
    order_id: int
    store_name: str
    pickup_barcode: str
    status: str
    total_amount: int
    payment_method: str
    payment_status: str
    created_at: datetime
