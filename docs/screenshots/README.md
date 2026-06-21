# 실제 Flet 실행 화면

- `00_login.png`: 데모 로그인 화면
- `01_nearby.png`: 위치 기준 거리순 편의점 조회
- `02_store_products.png`: 매장별 상품·가격·재고·이미지·진열 위치
- `03_product_compare.png`: 동일 상품의 매장별 가격·재고 비교
- `04_cart.png`: 장바구니 수량과 가상 결제
- `05_orders.png`: 주문 상태와 픽업 바코드
- `06_admin.png`: 상품·재고 CRUD
- `07_stock_validation_error.png`: 장바구니 생성 후 재고가 감소한 상황에서 주문 직전 재검증으로 결제를 중단한 화면

이 이미지는 `tools/capture_screenshots.py`가 Flet의 실제 숨김 렌더러와 `Page.take_screenshot()`을 사용해 생성한다. `docs/ui_design/`의 구현 전 와이어프레임과 구분해 보고서 구현 장에 사용한다.
