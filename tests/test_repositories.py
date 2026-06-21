from app.repositories.cart_repository import CartRepository
from app.repositories.order_repository import OrderRepository
from app.repositories.product_repository import ProductRepository
from app.repositories.store_repository import StoreRepository
from app.repositories.user_repository import UserRepository
from app.services.kimbap_service import KimbapService


def build_service(database):
    users = UserRepository(database)
    stores = StoreRepository(database)
    products = ProductRepository(database)
    carts = CartRepository(database)
    orders = OrderRepository(database)
    return KimbapService(users, stores, products, carts, orders), products, carts, orders


def test_login_and_nearby_store_search(database):
    service, _, _, _ = build_service(database)
    assert service.login("demo", "1234")["user_name"] == "데모 사용자"
    stores = service.nearby_stores(36.1456, 128.3935)
    assert len(stores) == 4
    assert stores == sorted(stores, key=lambda store: store.distance_meters)


def test_four_table_join_and_product_search(database):
    _, products, _, _ = build_service(database)
    rows = products.find_by_store(3, "햇반")
    assert rows
    assert all(row.store_id == 3 and "햇반" in row.product_name for row in rows)
    assert all(row.category_name for row in rows)


def test_left_join_keeps_unlisted_products(database):
    _, products, _, _ = build_service(database)
    rows = products.compare_by_product()
    assert len([row for row in rows if row.store_id is None]) == 5


def test_cart_order_transaction_decrements_stock(database):
    service, products, carts, orders = build_service(database)
    carts.add_item(user_id=2, store_id=3, product_id=1, quantity=1)
    before = products.find_by_store(3, "햇반 백미밥")[0].stock_count
    order_id = service.place_order(2, "CARD")
    after = products.find_by_store(3, "햇반 백미밥")[0].stock_count
    assert order_id == 2
    assert before - after == 1
    assert carts.get_lines(2) == []
    assert orders.find_by_user(2)[0].status == "PENDING"


def test_product_and_inventory_crud(database):
    _, products, _, _ = build_service(database)
    product_id = products.create_product(1, "테스트 김밥", "과제 제조사", "1줄")
    products.upsert_inventory(3, product_id, 2900, 4, "냉장 1열")
    row = products.find_by_store(3, "테스트 김밥")[0]
    assert (row.selling_price, row.stock_count) == (2900, 4)
    products.update_inventory(3, product_id, 3000, 2, "냉장 2열")
    row = products.find_by_store(3, "테스트 김밥")[0]
    assert (row.selling_price, row.stock_count, row.shelf_location) == (3000, 2, "냉장 2열")
    products.delete_inventory(3, product_id)
    products.delete_product(product_id)
    assert products.compare_by_product("테스트 김밥") == []
