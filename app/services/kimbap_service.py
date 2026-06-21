from __future__ import annotations

from app.exceptions import ValidationError
from app.repositories.cart_repository import CartRepository
from app.repositories.order_repository import OrderRepository
from app.repositories.product_repository import ProductRepository
from app.repositories.store_repository import StoreRepository
from app.repositories.user_repository import UserRepository


class KimbapService:
    PAYMENT_METHODS = {"CARD", "KAKAO_PAY", "NAVER_PAY"}

    def __init__(self, users: UserRepository, stores: StoreRepository, products: ProductRepository,
                 carts: CartRepository, orders: OrderRepository) -> None:
        self.users = users
        self.stores = stores
        self.products = products
        self.carts = carts
        self.orders = orders

    def login(self, login_id: str, password: str) -> dict:
        if not login_id.strip() or not password:
            raise ValidationError("아이디와 비밀번호를 입력하세요.")
        user = self.users.authenticate(login_id, password)
        if user is None:
            raise ValidationError("아이디 또는 비밀번호가 올바르지 않습니다.")
        return user

    def nearby_stores(self, latitude: float, longitude: float, radius_meters: float = 2_000):
        if not (-90 <= latitude <= 90 and -180 <= longitude <= 180):
            raise ValidationError("위도 또는 경도 범위가 올바르지 않습니다.")
        return self.stores.find_nearby(latitude, longitude, radius_meters)

    def place_order(self, user_id: int, payment_method: str) -> int:
        method = payment_method.upper()
        if method not in self.PAYMENT_METHODS:
            raise ValidationError("지원하지 않는 결제 방법입니다.")
        return self.orders.place_from_cart(user_id, method)
