-- JOIN 1: 선택 매장의 상품·카테고리·가격·현재 재고
SELECT
    s.store_name,
    p.product_name,
    c.category_name,
    i.selling_price,
    i.stock_count,
    i.shelf_location,
    p.image_path,
    i.updated_at
FROM stores AS s
JOIN inventories AS i ON i.store_id = s.store_id
JOIN products AS p ON p.product_id = i.product_id
JOIN categories AS c ON c.category_id = p.category_id
WHERE s.store_id = ?
ORDER BY c.display_order, p.product_name;
