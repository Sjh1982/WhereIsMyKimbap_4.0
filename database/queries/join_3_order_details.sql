-- JOIN 3: 주문·사용자·매장·상세상품·결제 내역
SELECT
    o.order_id,
    u.user_name,
    s.store_name,
    p.product_name,
    oi.quantity,
    oi.ordered_price,
    oi.quantity * oi.ordered_price AS line_total,
    pay.payment_method,
    pay.status AS payment_status,
    o.status AS order_status,
    o.pickup_barcode,
    o.created_at
FROM orders AS o
JOIN users AS u ON u.user_id = o.user_id
JOIN stores AS s ON s.store_id = o.store_id
JOIN order_items AS oi ON oi.order_id = o.order_id
JOIN products AS p ON p.product_id = oi.product_id
JOIN payments AS pay ON pay.order_id = o.order_id
WHERE o.user_id = ?
ORDER BY o.created_at DESC, o.order_id, p.product_name;
