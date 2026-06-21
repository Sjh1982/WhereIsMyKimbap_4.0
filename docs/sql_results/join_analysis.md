# 주요 JOIN 실행 분석

## JOIN 1 — 매장별 상품·재고

- SQL: `database/queries/join_1_store_products.sql`
- 테이블: stores, inventories, products, categories
- 종류: 모두 반드시 존재해야 화면에 판매 상품으로 표시되므로 INNER JOIN.
- 실행 조건: `store_id = 3`(CU 금오공대 정문점).
- Flet 위치: 매장 상품 화면 `KimbapApplication.render_store_products()`.

## JOIN 2 — 상품별 매장 비교

- SQL: `database/queries/join_2_product_store_comparison.sql`
- 테이블: products, categories, inventories, stores
- 종류: 상품 카탈로그를 기준으로 취급 매장이 없는 상품도 유지해야 하므로 inventories와 stores를 LEFT JOIN.
- 실행 조건: 전체 상품(`%`). PNG 상단에는 LEFT JOIN의 핵심인 취급 매장 `NULL` 행을 우선 표시한다.
- Flet 위치: 상품 비교 화면 `KimbapApplication.render_comparison()`.

## JOIN 3 — 주문·결제 상세

- SQL: `database/queries/join_3_order_details.sql`
- 테이블: orders, users, stores, order_items, products, payments
- 종류: 완료된 주문의 필수 관계만 표시하므로 INNER JOIN.
- 실행 조건: `user_id = 1`(demo).
- Flet 위치: 주문 내역 화면과 주문 상세 보고서 증빙.

각 실행 결과의 전체 행은 CSV, 앞 12행은 같은 이름의 PNG로 보존한다. 가격·재고·결제는 과제용 예시 데이터다.
