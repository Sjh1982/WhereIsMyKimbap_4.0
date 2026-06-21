# Crow’s Feet ERD

ERD는 `database/schema.sql`의 10개 테이블과 외래키를 기준으로 생성했다.

- 편집 원본: `where_is_my_kimbap_4.0.erd.json`
- 보고서용 이미지: `where_is_my_kimbap_4.0_erd.png`
- `inventories`: stores N:M products 관계 해소
- `cart_items`: carts N:M products 관계 해소
- `order_items`: orders N:M products 관계 해소
- `payments`: 각 payment는 정확히 한 order에 속하고, order는 커밋 상태에서 payment를 0개 또는 1개 가진다(1:0..1).

부모 Entity 하나에 자식 행이 아직 없을 수 있으므로 일반적인 부모-자식 관계는 DB 제약 기준 `1:0..N`으로 표시한다. `users.user_id`에 대한 `carts.user_id` UNIQUE와 `payments.order_id` UNIQUE는 각각 자식의 최대 개수를 1로 제한한다.

JSON은 VSCode ERD Editor 3.x 스키마 형식이며 PNG는 Crow’s Feet의 1:N 관계를 표시한다.
