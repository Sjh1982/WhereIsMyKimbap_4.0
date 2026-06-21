"""Capture the real Flet stock-validation failure without modifying the app DB."""
from __future__ import annotations

import asyncio
import sys
from pathlib import Path

import flet as ft

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.config import ASSETS_DIR
from app.database import Database
from app.repositories.cart_repository import CartRepository
from app.repositories.order_repository import OrderRepository
from app.repositories.product_repository import ProductRepository
from app.repositories.store_repository import StoreRepository
from app.repositories.user_repository import UserRepository
from app.services.kimbap_service import KimbapService
from app.views.application import KimbapApplication

TEST_DB = ROOT / "database" / "test_stock_validation.duckdb"
OUTPUT = ROOT / "docs" / "screenshots" / "07_stock_validation_error.png"


async def capture(page: ft.Page) -> None:
    page.enable_screenshots = True
    page.window.width = 1440
    page.window.height = 900

    database = Database(TEST_DB)
    database.initialize(seed=True)
    users = UserRepository(database)
    stores = StoreRepository(database)
    products = ProductRepository(database)
    carts = CartRepository(database)
    orders = OrderRepository(database)
    service = KimbapService(users, stores, products, carts, orders)

    # demo 장바구니에는 상품 1이 1개 담겨 있다. 결제 직전 재고를 0으로 바꿔
    # 장바구니 생성 이후 재고가 변한 현실적인 경쟁 상황을 재현한다.
    products.update_inventory(3, 1, 3600, 0, "2번 진열대 A열")

    app = KimbapApplication(page, service, stores, products, carts, orders)
    app.start()
    app.user = service.login("demo", "1234")
    app.show_shell()
    app.rail.selected_index = 3
    app.render_cart()

    # 보고서 캡처에서는 실제 장바구니 카드가 한 화면에 보이도록 배치한다.
    listing = app.content.content.controls[1]
    app.content.content.controls[1] = ft.Column(listing.controls, spacing=8)
    page.update()

    # 실제 주문 Service를 호출한다. OrderRepository가 현재 재고를 다시 검사하고
    # InsufficientStockError를 발생시키며 UI는 사용자용 SnackBar를 표시한다.
    app.guard(lambda: service.place_order(1, "CARD"))
    await asyncio.sleep(0.8)
    OUTPUT.write_bytes(await page.take_screenshot(pixel_ratio=1))
    print(OUTPUT)
    await page.window.close()


if __name__ == "__main__":
    try:
        if TEST_DB.exists():
            TEST_DB.unlink()
        ft.run(capture, view=ft.AppView.FLET_APP_HIDDEN, assets_dir=str(ASSETS_DIR))
    finally:
        if TEST_DB.exists():
            TEST_DB.unlink()
