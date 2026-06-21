# 관계형 스키마

- users(`user_id` PK, `login_id` UQ, password_hash, user_name, role, created_at)
- stores(`store_id` PK, `source_store_key` UQ, `store_name` UQ, brand, address, latitude, longitude, opening_hours, image_path, is_active)
- categories(`category_id` PK, `category_name` UQ, `display_order` UQ)
- products(`product_id` PK, `category_id` FK, product_name, manufacturer, package_size, description, image_path, is_limited, UQ(product_name, manufacturer, package_size))
- inventories(`store_id` PK/FK, `product_id` PK/FK, selling_price, stock_count, shelf_location, updated_at)
- carts(`cart_id` PK, `user_id` FK/UQ, `store_id` FK, created_at, updated_at)
- cart_items(`cart_id` PK/FK, `product_id` PK/FK, quantity, added_at)
- orders(`order_id` PK, `user_id` FK, `store_id` FK, `pickup_barcode` UQ, status, total_amount, created_at, picked_up_at, canceled_at)
- order_items(`order_id` PK/FK, `product_id` PK/FK, quantity, ordered_price)
- payments(`payment_id` PK, `order_id` FK/UQ, amount, payment_method, status, paid_at, refunded_at)

`inventories`, `cart_items`, `order_items`는 각각 두 Entity의 N:M 관계를 해소하는 Relationship 테이블이다.
