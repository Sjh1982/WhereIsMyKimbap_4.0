# Where Is My Kimbap? 4.0

금오공대 주변 편의점의 상품과 재고를 찾고, 한 매장의 상품을 장바구니에 담아 주문·결제·픽업까지 체험하는 Python 데스크톱 앱이다.

Public Repository: https://github.com/Sjh1982/WhereIsMyKimbap_4.0

## 기술 구성

- Python 3.13
- Flet GUI
- DuckDB
- View → Service → Repository → DuckDB
- pytest 자동 테스트

## 상태

핵심 DB, Repository, Service, Flet GUI와 CRUD를 구현했다. `WhereIsMyKimbap_3.0`과 `CampusConvenienceFinder`는 읽기 전용 참고 자료이며 이 프로젝트에서 수정하지 않는다.

## 실행 방법

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python main.py
```

데모 계정은 `demo / 1234`, 관리자 계정은 `admin / admin1234`다. 관리자 계정에서는 상품과 매장별 재고 관계 CRUD 화면이 추가된다.

웹 모드로 확인하려면 다음 명령을 사용한다.

```powershell
flet run --web -a assets main.py
```

## 핵심 기능

- 데모 사용자 로그인
- 현재 위치 기준 편의점 거리순 조회
- 상품 검색 및 매장별 가격·재고 비교
- 장바구니 추가·수량 수정·삭제
- 재고 검증을 포함한 주문과 가상 결제
- 픽업 바코드와 주문 상태 조회
- 상품·재고 관리 CRUD

## 테스트

```powershell
python -m pytest -q
```

현재 자동 테스트는 스키마·중복 시드·제약조건·JOIN·LEFT JOIN·로그인·거리 계산·장바구니 주문·CRUD·이미지 fallback을 검증한다.

## 설계와 증빙

- Crow's Feet ERD와 ERD Editor 원본: `docs/erd/`
- 관계형 스키마와 BCNF: `docs/logical_design/`
- Use Case, Sequence, Repository Interface, 전체 구성도: `docs/`
- 구현 전 와이어프레임 6개: `docs/ui_design/`
- 실제 Flet 실행 화면 8개: `docs/screenshots/`
- JOIN SQL, 전체 CSV, 보고서용 PNG: `database/queries/`, `docs/sql_results/`

증빙 자료를 다시 만들려면 다음을 실행한다.

```powershell
python tools/build_design_assets.py
python tools/export_sql_evidence.py
python tools/capture_screenshots.py
```

가격·재고·결제는 과제용 예시 데이터이며 실제 POS 또는 결제망과 연결되지 않는다.
