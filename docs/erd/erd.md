# Crow’s Feet ERD

ERD는 `database/schema.sql`의 10개 테이블과 외래키를 기준으로 생성했다.

- 편집 원본: `where_is_my_kimbap_4.0.erd.json`
- 보고서용 이미지: `where_is_my_kimbap_4.0_erd.png`
- `inventories`: stores N:M products 관계 해소
- `cart_items`: carts N:M products 관계 해소
- `order_items`: orders N:M products 관계 해소
- `payments`: orders와 1:1

JSON은 VSCode ERD Editor 3.x 스키마 형식이며 PNG는 Crow’s Feet의 1:N 관계를 표시한다.
