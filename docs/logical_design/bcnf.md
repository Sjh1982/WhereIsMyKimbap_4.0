# BCNF 검토

BCNF 조건은 모든 비자명 함수 종속 `X → Y`에서 결정자 X가 후보키인 것이다.

- users: `user_id → 모든 속성`, `login_id → 모든 속성`. 두 결정자 모두 후보키다.
- stores: `store_id`, `source_store_key`, `store_name`이 각각 후보키이며 비키 속성을 결정한다.
- categories: `category_id`, `category_name`, `display_order`가 후보키다.
- products: `product_id`와 `(product_name, manufacturer, package_size)`가 후보키다. category_name은 categories로 분리해 이행 종속을 제거했다.
- inventories: `(store_id, product_id) → selling_price, stock_count, shelf_location, updated_at`. 결정자가 복합 후보키다.
- carts: `cart_id → 모든 속성`, `user_id → 모든 속성`. 사용자당 활성 장바구니 하나라는 업무 규칙으로 둘 다 후보키다.
- cart_items: `(cart_id, product_id) → quantity, added_at`.
- orders: `order_id → 모든 속성`, `pickup_barcode → 모든 속성`.
- order_items: `(order_id, product_id) → quantity, ordered_price`. 주문 시점 가격은 상품 현재값과 독립된 스냅샷이다.
- payments: `payment_id → 모든 속성`, `order_id → 모든 속성`. 주문당 결제 한 건 규칙으로 둘 다 후보키다.

따라서 각 릴레이션의 의미 있는 결정자는 후보키이며 10개 테이블은 BCNF를 만족한다. 표시용 재고 상태는 저장하지 않고 `stock_count`에서 계산해 갱신 이상을 피한다.
