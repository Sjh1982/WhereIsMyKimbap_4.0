CREATE TABLE IF NOT EXISTS users (
    user_id BIGINT PRIMARY KEY,
    login_id VARCHAR NOT NULL UNIQUE CHECK (length(trim(login_id)) > 0),
    password_hash VARCHAR NOT NULL CHECK (length(trim(password_hash)) > 0),
    user_name VARCHAR NOT NULL CHECK (length(trim(user_name)) > 0),
    role VARCHAR NOT NULL DEFAULT 'CUSTOMER' CHECK (role IN ('CUSTOMER', 'ADMIN')),
    created_at TIMESTAMP NOT NULL
);

CREATE TABLE IF NOT EXISTS stores (
    store_id BIGINT PRIMARY KEY,
    source_store_key VARCHAR NOT NULL UNIQUE CHECK (length(trim(source_store_key)) > 0),
    store_name VARCHAR NOT NULL UNIQUE CHECK (length(trim(store_name)) > 0),
    brand VARCHAR NOT NULL CHECK (length(trim(brand)) > 0),
    address VARCHAR NOT NULL CHECK (length(trim(address)) > 0),
    latitude DOUBLE NOT NULL CHECK (latitude BETWEEN -90 AND 90),
    longitude DOUBLE NOT NULL CHECK (longitude BETWEEN -180 AND 180),
    opening_hours VARCHAR,
    image_path VARCHAR NOT NULL CHECK (
        length(trim(image_path)) > 0
        AND image_path NOT LIKE '/%'
        AND image_path NOT LIKE '\\%'
        AND image_path NOT LIKE '%:%'
    ),
    is_active BOOLEAN NOT NULL DEFAULT TRUE
);

CREATE TABLE IF NOT EXISTS categories (
    category_id BIGINT PRIMARY KEY,
    category_name VARCHAR NOT NULL UNIQUE CHECK (length(trim(category_name)) > 0),
    display_order INTEGER NOT NULL UNIQUE CHECK (display_order >= 0)
);

CREATE TABLE IF NOT EXISTS products (
    product_id BIGINT PRIMARY KEY,
    category_id BIGINT NOT NULL REFERENCES categories(category_id),
    product_name VARCHAR NOT NULL CHECK (length(trim(product_name)) > 0),
    manufacturer VARCHAR NOT NULL CHECK (length(trim(manufacturer)) > 0),
    package_size VARCHAR NOT NULL CHECK (length(trim(package_size)) > 0),
    description VARCHAR,
    image_path VARCHAR NOT NULL CHECK (
        length(trim(image_path)) > 0
        AND image_path NOT LIKE '/%'
        AND image_path NOT LIKE '\\%'
        AND image_path NOT LIKE '%:%'
    ),
    is_limited BOOLEAN NOT NULL DEFAULT FALSE,
    UNIQUE(product_name, manufacturer, package_size)
);

-- stores와 products의 N:M Relationship. 매장별 가격과 현재 재고를 보관한다.
CREATE TABLE IF NOT EXISTS inventories (
    store_id BIGINT NOT NULL REFERENCES stores(store_id),
    product_id BIGINT NOT NULL REFERENCES products(product_id),
    selling_price INTEGER NOT NULL CHECK (selling_price >= 0),
    stock_count INTEGER NOT NULL CHECK (stock_count >= 0),
    shelf_location VARCHAR NOT NULL CHECK (length(trim(shelf_location)) > 0),
    updated_at TIMESTAMP NOT NULL,
    PRIMARY KEY (store_id, product_id)
);

CREATE TABLE IF NOT EXISTS carts (
    cart_id BIGINT PRIMARY KEY,
    user_id BIGINT NOT NULL UNIQUE REFERENCES users(user_id),
    store_id BIGINT NOT NULL REFERENCES stores(store_id),
    created_at TIMESTAMP NOT NULL,
    updated_at TIMESTAMP NOT NULL
);

-- carts와 products의 N:M Relationship.
CREATE TABLE IF NOT EXISTS cart_items (
    cart_id BIGINT NOT NULL REFERENCES carts(cart_id),
    product_id BIGINT NOT NULL REFERENCES products(product_id),
    quantity INTEGER NOT NULL CHECK (quantity > 0),
    added_at TIMESTAMP NOT NULL,
    PRIMARY KEY (cart_id, product_id)
);

CREATE TABLE IF NOT EXISTS orders (
    order_id BIGINT PRIMARY KEY,
    user_id BIGINT NOT NULL REFERENCES users(user_id),
    store_id BIGINT NOT NULL REFERENCES stores(store_id),
    pickup_barcode VARCHAR NOT NULL UNIQUE CHECK (length(trim(pickup_barcode)) = 8),
    status VARCHAR NOT NULL CHECK (status IN ('PENDING', 'PICKED_UP', 'CANCELED')),
    total_amount INTEGER NOT NULL CHECK (total_amount >= 0),
    created_at TIMESTAMP NOT NULL,
    picked_up_at TIMESTAMP,
    canceled_at TIMESTAMP
);

-- orders와 products의 N:M Relationship이며 주문 시점 가격을 스냅샷으로 보존한다.
CREATE TABLE IF NOT EXISTS order_items (
    order_id BIGINT NOT NULL REFERENCES orders(order_id),
    product_id BIGINT NOT NULL REFERENCES products(product_id),
    quantity INTEGER NOT NULL CHECK (quantity > 0),
    ordered_price INTEGER NOT NULL CHECK (ordered_price >= 0),
    PRIMARY KEY (order_id, product_id)
);

CREATE TABLE IF NOT EXISTS payments (
    payment_id BIGINT PRIMARY KEY,
    order_id BIGINT NOT NULL UNIQUE REFERENCES orders(order_id),
    amount INTEGER NOT NULL CHECK (amount >= 0),
    payment_method VARCHAR NOT NULL CHECK (payment_method IN ('CARD', 'KAKAO_PAY', 'NAVER_PAY')),
    status VARCHAR NOT NULL CHECK (status IN ('PAID', 'REFUNDED')),
    paid_at TIMESTAMP NOT NULL,
    refunded_at TIMESTAMP
);
