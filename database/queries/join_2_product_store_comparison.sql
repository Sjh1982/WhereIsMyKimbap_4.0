-- JOIN 2: products 기준 LEFT JOIN으로 취급 매장이 없는 상품도 유지
SELECT
    p.product_id,
    p.product_name,
    c.category_name,
    s.store_name,
    i.selling_price,
    i.stock_count,
    i.updated_at
FROM products AS p
JOIN categories AS c ON c.category_id = p.category_id
LEFT JOIN inventories AS i ON i.product_id = p.product_id
LEFT JOIN stores AS s ON s.store_id = i.store_id
WHERE lower(p.product_name) LIKE lower(?)
ORDER BY p.product_name, i.selling_price NULLS LAST, s.store_name;
