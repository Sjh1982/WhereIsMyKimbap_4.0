# 스키마 변경 기록

## 2026-06-21 — 4.0 최초 설계

- MySQL 전용 `AUTO_INCREMENT`, `CREATE DATABASE`, `ON DUPLICATE KEY`를 제거했다.
- 사용자, 매장, 카테고리, 상품, 재고, 장바구니, 주문, 결제를 10개 테이블로 분리했다.
- `inventories`, `cart_items`, `order_items`를 Entity 간 Relationship 테이블로 명확히 설계했다.
- 매장별 판매가격을 표현하기 위해 `inventories.selling_price`를 추가했다.
- 주문 당시 가격을 보존하도록 `order_items.ordered_price`를 두었다.
- DB 이미지 값은 프로젝트 내부 상대경로만 허용한다.
- 필수 문자열의 빈 문자열과 음수 가격·재고·수량을 CHECK로 차단한다.
