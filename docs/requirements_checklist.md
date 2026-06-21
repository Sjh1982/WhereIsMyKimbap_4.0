# Where Is My Kimbap? 4.0 요구사항 체크리스트

## 프로젝트 경계

- 신규 작업 위치: `C:\db2026\WhereIs\WhereIsMyKimbap_4.0`
- `WhereIsMyKimbap_3.0`: 읽기 전용 기능·데이터 참고
- `CampusConvenienceFinder`: 폐기된 주제의 보존본, 수정하지 않음
- 작업공간 루트 기존 파일: 수정하지 않음

## 4.0 기능 범위

| ID | 요구사항 | 상태 |
|---|---|---|
| F-01 | 데모 로그인 | 구현·테스트 |
| F-02 | 위치 기준 가까운 편의점 조회 | 구현·테스트 |
| F-03 | 상품명·카테고리 검색 | 구현·테스트 |
| F-04 | 매장별 상품·가격·재고 JOIN 조회 | 구현·테스트 |
| F-05 | 상품별 매장 재고 LEFT JOIN 비교 | 구현·테스트 |
| F-06 | 장바구니 추가·수정·삭제 | 구현·테스트 |
| F-07 | 주문·가상 결제·재고 차감 트랜잭션 | 구현·테스트 |
| F-08 | 픽업 처리와 주문 내역 | 구현·테스트 |
| F-09 | 상품·재고 관리 CRUD | 구현·테스트 |
| F-10 | 이미지 상대경로 저장과 fallback | 구현·테스트 |

## 과제 증빙

| ID | 요구사항 | 산출물 |
|---|---|---|
| DB-01 | Entity 2개 + Relationship 1개 이상 DDL/삽입 | 완료: `database/schema.sql`, `database/seed.sql` |
| DB-02 | 세 테이블 이상 JOIN | SQL·CSV·PNG 실행 증빙 완료 |
| DB-03 | Crow's Feet ERD와 관계형 스키마 | JSON·PNG·Markdown 완료 |
| DB-04 | BCNF 설명 | 완료 |
| UI-01 | Flet 실행 화면 | 실제 렌더러 PNG 7개 완료 |
| IMG-01 | DB 이미지 경로와 Flet 출력 | 구현·테스트 완료 |
| TEST-01 | 스키마·시드·CRUD·JOIN·주문 테스트 | 11개 통과 |
| GIT-01 | GitHub Public Repository 공개 | `Sjh1982/WhereIsMyKimbap_4.0` 완료 |

## 3.0에서 유지·개선할 핵심

- 유지: 매장 검색, 상품 재고, 장바구니, 주문, 결제, 픽업 바코드.
- 개선: MySQL 의존 제거, 웹 프런트 제거, Flet 단일 GUI, 계층 분리, SQL 제약조건 강화, 재현 가능한 시드와 테스트.
- 결제와 바코드는 학습용 시뮬레이션이며 실제 외부 서비스와 연동하지 않는다.
