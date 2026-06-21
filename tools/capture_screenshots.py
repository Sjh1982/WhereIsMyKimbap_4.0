"""Capture actual Flet implementation screens with Flet's renderer."""
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

OUTPUT = ROOT / "docs" / "screenshots"


async def capture_main(page: ft.Page) -> None:
    page.enable_screenshots = True
    page.window.width = 1440
    page.window.height = 900
    database = Database()
    database.initialize(seed=True)
    users = UserRepository(database)
    stores = StoreRepository(database)
    products = ProductRepository(database)
    carts = CartRepository(database)
    orders = OrderRepository(database)
    service = KimbapService(users, stores, products, carts, orders)
    app = KimbapApplication(page, service, stores, products, carts, orders)
    app.start()
    OUTPUT.mkdir(parents=True, exist_ok=True)

    await asyncio.sleep(1.2)
    (OUTPUT / "00_login.png").write_bytes(await page.take_screenshot(pixel_ratio=1))

    app.user = service.login("demo", "1234")
    app.show_shell()
    screens = [
        ("01_nearby.png", app.render_nearby, 0),
        ("02_store_products.png", app.render_store_products, 1),
        ("03_product_compare.png", app.render_comparison, 2),
        ("04_cart.png", app.render_cart, 3),
        ("05_orders.png", app.render_orders, 4),
        ("06_admin.png", app.render_admin, 5),
    ]
    for filename, renderer, index in screens:
        if filename == "06_admin.png":
            app.user = service.login("admin", "admin1234")
            app.show_shell()
        app.rail.selected_index = index
        renderer()
        # 긴 목록 대신 실제 검색 기능으로 대표 결과를 좁혀 보고서에서 카드 내용을 읽을 수 있게 한다.
        if filename == "02_store_products.png":
            keyword = app.content.content.controls[1].controls[2]
            keyword.value = "햇반 백미밥"
            keyword.on_submit(None)
            app.content.content.controls[2].scroll = None
            app.content.content.controls[2].expand = False
        elif filename == "03_product_compare.png":
            keyword = app.content.content.controls[1].controls[0]
            keyword.value = "김치 사발면"
            keyword.on_submit(None)
            app.content.content.controls[2].scroll = None
            app.content.content.controls[2].expand = False
        elif filename == "01_nearby.png":
            listing = app.content.content.controls[2]
            app.content.content.controls[2] = ft.Column(listing.controls[:4], spacing=8)
        elif filename in {"04_cart.png", "05_orders.png"}:
            listing = app.content.content.controls[1]
            app.content.content.controls[1] = ft.Column(listing.controls, spacing=8)
        page.update()
        await asyncio.sleep(0.45)
        (OUTPUT / filename).write_bytes(await page.take_screenshot(pixel_ratio=1))
        print(filename)
    await page.window.close()


if __name__ == "__main__":
    ft.run(capture_main, view=ft.AppView.FLET_APP_HIDDEN, assets_dir=str(ASSETS_DIR))
