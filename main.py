import flet as ft

from app.config import ASSETS_DIR
from app.database import Database
from app.repositories.cart_repository import CartRepository
from app.repositories.order_repository import OrderRepository
from app.repositories.product_repository import ProductRepository
from app.repositories.store_repository import StoreRepository
from app.repositories.user_repository import UserRepository
from app.services.kimbap_service import KimbapService
from app.views.application import KimbapApplication


def main(page: ft.Page) -> None:
    database = Database()
    database.initialize(seed=True)
    users = UserRepository(database)
    stores = StoreRepository(database)
    products = ProductRepository(database)
    carts = CartRepository(database)
    orders = OrderRepository(database)
    service = KimbapService(users, stores, products, carts, orders)
    KimbapApplication(page, service, stores, products, carts, orders).start()


if __name__ == "__main__":
    ft.run(main, assets_dir=str(ASSETS_DIR))
