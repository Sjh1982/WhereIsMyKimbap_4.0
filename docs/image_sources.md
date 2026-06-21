# 이미지 출처

- `assets/images/default_store.png`: 프로젝트용으로 생성한 기본 매장 이미지. 브랜드 로고나 외부 hot-link를 사용하지 않는다.
- `assets/images/default_product.png`: 프로젝트용으로 생성한 기본 상품 이미지. 특정 제조사의 포장을 복제하지 않는다.

두 이미지는 이전 내부 시제품에서 제작한 자체 자산을 4.0 프로젝트에 복사해 사용했다. DB에는 `assets/images/...` 상대경로만 저장하며, Flet에는 assets 루트 기준 `images/...`로 변환해 전달한다.
