from __future__ import annotations

import flet as ft

from app.config import DEFAULT_LATITUDE, DEFAULT_LONGITUDE
from app.exceptions import AppError
from app.repositories.cart_repository import CartRepository
from app.repositories.order_repository import OrderRepository
from app.repositories.product_repository import ProductRepository
from app.repositories.store_repository import StoreRepository
from app.services.image_service import ImageService
from app.services.kimbap_service import KimbapService


class KimbapApplication:
    def __init__(self, page: ft.Page, service: KimbapService, stores: StoreRepository,
                 products: ProductRepository, carts: CartRepository, orders: OrderRepository) -> None:
        self.page = page
        self.service = service
        self.stores = stores
        self.products = products
        self.carts = carts
        self.orders = orders
        self.images = ImageService()
        self.user: dict | None = None
        self.selected_store_id = 3
        self.content = ft.Container(expand=True, padding=20)
        self.rail: ft.NavigationRail | None = None

    def start(self) -> None:
        self.page.title = "Where Is My Kimbap? 4.0"
        self.page.theme_mode = ft.ThemeMode.LIGHT
        self.page.theme = ft.Theme(color_scheme_seed=ft.Colors.GREEN_600)
        self.page.padding = 0
        self.show_login()

    def notify(self, message: str, error: bool = False) -> None:
        self.page.show_dialog(ft.SnackBar(message, bgcolor=ft.Colors.RED_700 if error else ft.Colors.GREEN_700))

    def guard(self, action, success: str | None = None) -> None:
        try:
            action()
            if success:
                self.notify(success)
        except (AppError, ValueError) as exc:
            self.notify(str(exc), error=True)
        except Exception as exc:
            print(f"[UI] 예기치 않은 오류: {exc}")
            self.notify("처리 중 오류가 발생했습니다. 콘솔의 원인을 확인하세요.", error=True)

    def show_login(self) -> None:
        login_id = ft.TextField(label="아이디", value="demo", width=320, autofocus=True)
        password = ft.TextField(label="비밀번호", value="1234", password=True, can_reveal_password=True, width=320)

        def submit(_=None) -> None:
            def action() -> None:
                self.user = self.service.login(login_id.value or "", password.value or "")
                self.show_shell()
            self.guard(action)

        password.on_submit = submit
        panel = ft.Card(
            content=ft.Container(
                width=430,
                padding=36,
                content=ft.Column([
                    ft.Icon(ft.Icons.LOCATION_ON, size=54, color=ft.Colors.GREEN_700),
                    ft.Text("Where Is My Kimbap?", size=28, weight=ft.FontWeight.BOLD),
                    ft.Text("주변 편의점 재고를 찾고 픽업 주문을 체험하세요.", color=ft.Colors.GREY_700),
                    login_id,
                    password,
                    ft.FilledButton("로그인", icon=ft.Icons.LOGIN, on_click=submit, width=320),
                    ft.Text("데모 계정: demo / 1234", size=12, color=ft.Colors.GREY_600),
                ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=16),
            )
        )
        self.page.controls.clear()
        self.page.add(ft.Container(content=panel, alignment=ft.Alignment.CENTER, expand=True, bgcolor=ft.Colors.GREEN_50))
        self.page.update()

    def show_shell(self) -> None:
        destinations = [
            ft.NavigationRailDestination(ft.Icons.STORE, label="주변 매장"),
            ft.NavigationRailDestination(ft.Icons.INVENTORY_2, label="매장 상품"),
            ft.NavigationRailDestination(ft.Icons.COMPARE_ARROWS, label="상품 비교"),
            ft.NavigationRailDestination(ft.Icons.SHOPPING_CART, label="장바구니"),
            ft.NavigationRailDestination(ft.Icons.RECEIPT_LONG, label="주문 내역"),
        ]
        if self.user and self.user["role"] == "ADMIN":
            destinations.append(ft.NavigationRailDestination(ft.Icons.ADMIN_PANEL_SETTINGS, label="데이터 관리"))
        self.rail = ft.NavigationRail(
            destinations=destinations,
            selected_index=0,
            extended=True,
            min_extended_width=190,
            on_change=self.change_view,
            leading=ft.Column([
                ft.Icon(ft.Icons.RICE_BOWL, color=ft.Colors.GREEN_700, size=34),
                ft.Text("WIMK 4.0", weight=ft.FontWeight.BOLD),
            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
            trailing=ft.TextButton("로그아웃", icon=ft.Icons.LOGOUT, on_click=lambda _: self.logout()),
        )
        self.page.controls.clear()
        self.page.add(ft.Row([self.rail, ft.VerticalDivider(width=1), self.content], expand=True, spacing=0))
        self.render_nearby()

    def logout(self) -> None:
        self.user = None
        self.show_login()

    def change_view(self, event) -> None:
        renderers = [self.render_nearby, self.render_store_products, self.render_comparison,
                     self.render_cart, self.render_orders, self.render_admin]
        renderers[event.control.selected_index]()

    def heading(self, title: str, subtitle: str) -> ft.Control:
        return ft.Column([
            ft.Text(title, size=26, weight=ft.FontWeight.BOLD),
            ft.Text(subtitle, color=ft.Colors.GREY_700),
            ft.Divider(),
        ], spacing=4)

    def app_image(self, path: str, kind: str, width: int = 88, height: int = 88) -> ft.Image:
        return ft.Image(
            src=self.images.resolve(path, kind), width=width, height=height,
            fit=ft.BoxFit.COVER, border_radius=10,
            error_content=ft.Icon(ft.Icons.BROKEN_IMAGE, size=36, color=ft.Colors.GREY_500),
        )

    def render_nearby(self) -> None:
        latitude = ft.TextField(label="위도", value=str(DEFAULT_LATITUDE), width=180)
        longitude = ft.TextField(label="경도", value=str(DEFAULT_LONGITUDE), width=180)
        results = ft.ListView(expand=True, spacing=10, padding=4, build_controls_on_demand=False)

        def select_store(store_id: int) -> None:
            self.selected_store_id = store_id
            self.rail.selected_index = 1
            self.render_store_products()

        def search(_=None) -> None:
            def action() -> None:
                stores = self.service.nearby_stores(float(latitude.value), float(longitude.value))
                results.controls = [
                    ft.Card(content=ft.Container(
                        padding=14,
                        on_click=lambda _, store_id=store.store_id: select_store(store_id),
                        content=ft.Row([
                            self.app_image(store.image_path, "store"),
                            ft.Column([
                                ft.Text(store.store_name, size=17, weight=ft.FontWeight.BOLD),
                                ft.Text(f"{store.brand} · {store.distance_meters:.0f}m"),
                                ft.Text(store.address, color=ft.Colors.GREY_700),
                                ft.Text(store.opening_hours or "영업시간 정보 없음", size=12),
                            ], expand=True),
                            ft.Icon(ft.Icons.CHEVRON_RIGHT),
                        ])
                    )) for store in stores
                ] or [ft.Text("반경 2km 안에 조회 가능한 매장이 없습니다.")]
                self.page.update()
            self.guard(action)

        self.content.content = ft.Column([
            self.heading("주변 편의점", "기본 좌표는 금오공대이며 좌표를 직접 바꿀 수 있습니다."),
            ft.Row([latitude, longitude, ft.FilledButton("거리순 조회", icon=ft.Icons.SEARCH, on_click=search)], wrap=True),
            results,
        ], expand=True)
        search()

    def render_store_products(self) -> None:
        stores = self.stores.find_all()
        store_dropdown = ft.Dropdown(
            label="편의점", value=str(self.selected_store_id), width=300,
            options=[ft.DropdownOption(str(store.store_id), store.store_name) for store in stores],
        )
        category = ft.Dropdown(
            label="카테고리", value="", width=190,
            options=[ft.DropdownOption("", "전체")] + [
                ft.DropdownOption(str(category_id), name) for category_id, name in self.products.categories()
            ],
        )
        keyword = ft.TextField(label="상품명 검색", width=240)
        results = ft.Column(expand=True, spacing=8, scroll=ft.ScrollMode.AUTO)

        def add(product_id: int) -> None:
            self.guard(lambda: self.carts.add_item(self.user["user_id"], self.selected_store_id, product_id), "장바구니에 담았습니다.")

        def search(_=None) -> None:
            self.selected_store_id = int(store_dropdown.value)
            rows = self.products.find_by_store(
                self.selected_store_id, keyword.value or "", int(category.value) if category.value else None
            )
            results.controls = [self.product_card(row, ft.FilledButton(
                "담기", icon=ft.Icons.ADD_SHOPPING_CART,
                disabled=row.stock_count == 0,
                on_click=lambda _, product_id=row.product_id: add(product_id),
            )) for row in rows] or [ft.Text("검색 조건에 맞는 상품이 없습니다.")]
            self.page.update()

        store_dropdown.on_select = search
        category.on_select = search
        keyword.on_submit = search
        self.content.content = ft.Column([
            self.heading("매장별 상품·현재 재고", "4개 테이블 JOIN으로 가격과 재고, 진열 위치를 조회합니다."),
            ft.Row([store_dropdown, category, keyword, ft.Button("검색", icon=ft.Icons.SEARCH, on_click=search)], wrap=True),
            results,
        ], expand=True)
        search()

    def product_card(self, row, action: ft.Control | None = None, show_store: bool = False) -> ft.Card:
        status_color = {
            "품절": ft.Colors.RED_700,
            "재고 부족": ft.Colors.ORANGE_700,
            "재고 있음": ft.Colors.GREEN_700,
            "재고 미등록": ft.Colors.GREY_600,
        }[row.stock_status]
        details = [
            ft.Text(row.product_name, size=16, weight=ft.FontWeight.BOLD),
            ft.Text(f"{row.category_name} · {row.manufacturer} · {row.package_size}", size=12),
        ]
        if show_store:
            details.append(ft.Text(row.store_name or "취급 매장 없음", color=ft.Colors.BLUE_GREY_700))
        details.extend([
            ft.Text("가격 미등록" if row.selling_price is None else f"{row.selling_price:,}원"),
            ft.Text(f"{row.stock_status}" + ("" if row.stock_count is None else f" ({row.stock_count}개)"), color=status_color),
            ft.Text(row.shelf_location or "진열 위치 없음", size=12, color=ft.Colors.GREY_700),
        ])
        controls: list[ft.Control] = [self.app_image(row.image_path, "product"), ft.Column(details, width=650)]
        if action:
            controls.append(action)
        return ft.Card(content=ft.Container(padding=12, content=ft.Row(controls, wrap=True)))

    def render_comparison(self) -> None:
        keyword = ft.TextField(label="상품명", width=300, value="김치")
        results = ft.Column(expand=True, spacing=8, scroll=ft.ScrollMode.AUTO)

        def search(_=None) -> None:
            rows = self.products.compare_by_product(keyword.value or "")
            results.controls = [self.product_card(row, show_store=True) for row in rows] or [ft.Text("검색 결과가 없습니다.")]
            self.page.update()

        keyword.on_submit = search
        self.content.content = ft.Column([
            self.heading("상품별 편의점 비교", "products 기준 LEFT JOIN으로 재고 미등록 상품도 유지합니다."),
            ft.Row([keyword, ft.FilledButton("비교", icon=ft.Icons.COMPARE_ARROWS, on_click=search)]),
            results,
        ], expand=True)
        search()

    def render_cart(self) -> None:
        lines = self.carts.get_lines(self.user["user_id"])
        payment = ft.Dropdown(
            label="결제 방법", value="CARD", width=190,
            options=[ft.DropdownOption("CARD", "카드"), ft.DropdownOption("KAKAO_PAY", "카카오페이"), ft.DropdownOption("NAVER_PAY", "네이버페이")],
        )

        def change(product_id: int, quantity: int) -> None:
            self.guard(lambda: self.carts.update_quantity(self.user["user_id"], product_id, quantity))
            self.render_cart()

        cards = [ft.Card(content=ft.Container(padding=12, content=ft.Row([
            ft.Column([
                ft.Text(line.product_name, weight=ft.FontWeight.BOLD),
                ft.Text(f"{line.selling_price:,}원 × {line.quantity} = {line.line_total:,}원"),
                ft.Text(line.store_name, size=12, color=ft.Colors.GREY_700),
            ], width=650),
            ft.IconButton(ft.Icons.REMOVE, on_click=lambda _, line=line: change(line.product_id, line.quantity - 1)),
            ft.Text(str(line.quantity)),
            ft.IconButton(ft.Icons.ADD, on_click=lambda _, line=line: change(line.product_id, line.quantity + 1)),
            ft.IconButton(ft.Icons.DELETE_OUTLINE, icon_color=ft.Colors.RED_600, on_click=lambda _, line=line: change(line.product_id, 0)),
        ], wrap=True))) for line in lines]
        total = sum(line.line_total for line in lines)

        def order(_=None) -> None:
            def action() -> None:
                order_id = self.service.place_order(self.user["user_id"], payment.value)
                self.notify(f"주문 #{order_id} 결제가 완료되었습니다.")
                self.rail.selected_index = 4
                self.render_orders()
            self.guard(action)

        self.content.content = ft.Column([
            self.heading("장바구니", "한 번의 주문에는 한 편의점의 상품만 담을 수 있습니다."),
            ft.ListView(cards or [ft.Text("장바구니가 비어 있습니다.")], expand=True, spacing=8, build_controls_on_demand=False),
            ft.Row([ft.Text(f"합계 {total:,}원", size=22, weight=ft.FontWeight.BOLD), payment,
                    ft.FilledButton("가상 결제", icon=ft.Icons.PAYMENT, disabled=not lines, on_click=order)], wrap=True),
        ], expand=True)
        self.page.update()

    def render_orders(self) -> None:
        orders = self.orders.find_by_user(self.user["user_id"])

        def pickup(order_id: int) -> None:
            self.guard(lambda: self.orders.pickup(order_id, self.user["user_id"]), "수령 완료 처리했습니다.")
            self.render_orders()

        cards = [ft.Card(content=ft.Container(padding=14, content=ft.Row([
            ft.Icon(ft.Icons.QR_CODE_2, size=52, color=ft.Colors.GREEN_700),
            ft.Column([
                ft.Text(f"주문 #{order.order_id} · {order.store_name}", weight=ft.FontWeight.BOLD),
                ft.Text(f"픽업 바코드  {order.pickup_barcode}", size=19),
                ft.Text(f"{order.total_amount:,}원 · {order.payment_method} · {order.status}"),
                ft.Text(str(order.created_at), size=12, color=ft.Colors.GREY_700),
            ], width=700),
            ft.FilledButton("수령 완료", disabled=order.status != "PENDING", on_click=lambda _, oid=order.order_id: pickup(oid)),
        ], wrap=True))) for order in orders]
        self.content.content = ft.Column([
            self.heading("주문·픽업 내역", "주문, 매장, 결제를 JOIN해 상태와 픽업 바코드를 표시합니다."),
            ft.ListView(cards or [ft.Text("주문 내역이 없습니다.")], expand=True, spacing=8, build_controls_on_demand=False),
        ], expand=True)
        self.page.update()

    def render_admin(self) -> None:
        if self.user["role"] != "ADMIN":
            self.content.content = ft.Text("관리자만 접근할 수 있습니다.")
            self.page.update()
            return
        categories = self.products.categories()
        category = ft.Dropdown(label="카테고리", value=str(categories[0][0]), width=180,
                               options=[ft.DropdownOption(str(cid), name) for cid, name in categories])
        name = ft.TextField(label="상품명", width=220)
        maker = ft.TextField(label="제조사", width=180)
        package = ft.TextField(label="포장 단위", width=140)
        store_id = ft.TextField(label="매장 ID", value="3", width=110)
        product_id = ft.TextField(label="상품 ID", width=110)
        price = ft.TextField(label="가격", width=120)
        stock = ft.TextField(label="재고", width=100)
        shelf = ft.TextField(label="진열 위치", width=180)

        def create_product(_=None) -> None:
            def action() -> None:
                new_id = self.products.create_product(int(category.value), name.value or "", maker.value or "", package.value or "")
                product_id.value = str(new_id)
            self.guard(action, "상품을 추가했습니다.")

        def save_inventory(_=None) -> None:
            self.guard(lambda: self.products.upsert_inventory(
                int(store_id.value), int(product_id.value), int(price.value), int(stock.value), shelf.value or ""
            ), "재고 관계를 저장했습니다.")

        def delete_inventory(_=None) -> None:
            self.guard(lambda: self.products.delete_inventory(int(store_id.value), int(product_id.value)), "재고 관계를 삭제했습니다.")

        def delete_product(_=None) -> None:
            self.guard(lambda: self.products.delete_product(int(product_id.value)), "상품을 삭제했습니다.")

        self.content.content = ft.Column([
            self.heading("데이터 관리", "상품과 매장별 가격·재고를 생성, 조회, 수정, 삭제합니다."),
            ft.Text("상품 생성", size=18, weight=ft.FontWeight.BOLD),
            ft.Row([category, name, maker, package, ft.FilledButton("상품 추가", icon=ft.Icons.ADD, on_click=create_product)], wrap=True),
            ft.Divider(),
            ft.Text("재고 생성·수정·삭제 / 상품 삭제", size=18, weight=ft.FontWeight.BOLD),
            ft.Row([store_id, product_id, price, stock, shelf], wrap=True),
            ft.Row([
                ft.FilledButton("재고 저장", icon=ft.Icons.SAVE, on_click=save_inventory),
                ft.Button("재고 삭제", icon=ft.Icons.DELETE_OUTLINE, on_click=delete_inventory),
                ft.Button("상품 삭제", icon=ft.Icons.DELETE_FOREVER, on_click=delete_product),
            ], wrap=True),
            ft.Text("연결된 재고·장바구니·주문이 있는 상품은 참조 무결성을 위해 삭제되지 않습니다.", color=ft.Colors.GREY_700),
        ], scroll=ft.ScrollMode.AUTO)
        self.page.update()
