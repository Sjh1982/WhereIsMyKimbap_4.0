# 주요 Sequence Diagram

## 주문·결제

1. 사용자가 Flet View에서 결제를 요청한다.
2. `KimbapService`가 결제수단을 검증한다.
3. `OrderRepository`가 DuckDB 트랜잭션을 시작한다.
4. carts, cart_items, inventories, products를 JOIN해 재고와 가격을 확인한다.
5. orders, order_items, payments를 삽입하고 inventories 재고를 차감한다.
6. cart_items를 비우고 COMMIT한다.
7. View는 주문번호와 픽업 바코드를 표시한다.

중간 오류가 발생하면 ROLLBACK하여 주문·결제·재고가 부분 반영되지 않게 한다.
