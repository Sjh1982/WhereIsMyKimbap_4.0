# Repository Interface 설계

| Repository | 주요 책임 |
|---|---|
| UserRepository | 로그인 ID와 비밀번호 해시 인증 |
| StoreRepository | 전체/활성 매장 조회, Haversine 거리순 검색 |
| ProductRepository | 상품 검색·비교 JOIN, 상품·재고 CRUD, 모델 변환 |
| CartRepository | 사용자 장바구니 조회, 수량·재고 검증, 추가·수정·삭제 |
| OrderRepository | 주문 트랜잭션, 재고 차감, 결제 저장, 주문 조회·픽업 |

Repository는 DuckDB 오류를 사용자 문구가 있는 애플리케이션 예외로 변환한다. View는 SQL을 직접 실행하지 않으며 Service 또는 Repository가 반환한 모델만 표시한다.
