"""Generate report-ready diagrams and low-fidelity wireframes for WIMK 4.0."""
from __future__ import annotations

import json
import time
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent.parent
FONT_REGULAR = Path(r"C:\Windows\Fonts\malgun.ttf")
FONT_BOLD = Path(r"C:\Windows\Fonts\malgunbd.ttf")


def font(size: int = 18, bold: bool = False):
    return ImageFont.truetype(str(FONT_BOLD if bold else FONT_REGULAR), size)


TABLES = {
    "users": [("user_id", "BIGINT", "PK"), ("login_id", "VARCHAR", "UQ"), ("password_hash", "VARCHAR", ""), ("user_name", "VARCHAR", ""), ("role", "VARCHAR", ""), ("created_at", "TIMESTAMP", "")],
    "stores": [("store_id", "BIGINT", "PK"), ("source_store_key", "VARCHAR", "UQ"), ("store_name", "VARCHAR", "UQ"), ("brand", "VARCHAR", ""), ("address", "VARCHAR", ""), ("latitude", "DOUBLE", ""), ("longitude", "DOUBLE", ""), ("opening_hours", "VARCHAR", ""), ("image_path", "VARCHAR", ""), ("is_active", "BOOLEAN", "")],
    "categories": [("category_id", "BIGINT", "PK"), ("category_name", "VARCHAR", "UQ"), ("display_order", "INTEGER", "UQ")],
    "products": [("product_id", "BIGINT", "PK"), ("category_id", "BIGINT", "FK"), ("product_name", "VARCHAR", ""), ("manufacturer", "VARCHAR", ""), ("package_size", "VARCHAR", ""), ("description", "VARCHAR", ""), ("image_path", "VARCHAR", ""), ("is_limited", "BOOLEAN", "")],
    "inventories": [("store_id", "BIGINT", "PK/FK"), ("product_id", "BIGINT", "PK/FK"), ("selling_price", "INTEGER", ""), ("stock_count", "INTEGER", ""), ("shelf_location", "VARCHAR", ""), ("updated_at", "TIMESTAMP", "")],
    "carts": [("cart_id", "BIGINT", "PK"), ("user_id", "BIGINT", "FK/UQ"), ("store_id", "BIGINT", "FK"), ("created_at", "TIMESTAMP", ""), ("updated_at", "TIMESTAMP", "")],
    "cart_items": [("cart_id", "BIGINT", "PK/FK"), ("product_id", "BIGINT", "PK/FK"), ("quantity", "INTEGER", ""), ("added_at", "TIMESTAMP", "")],
    "orders": [("order_id", "BIGINT", "PK"), ("user_id", "BIGINT", "FK"), ("store_id", "BIGINT", "FK"), ("pickup_barcode", "VARCHAR", "UQ"), ("status", "VARCHAR", ""), ("total_amount", "INTEGER", ""), ("created_at", "TIMESTAMP", ""), ("picked_up_at", "TIMESTAMP", ""), ("canceled_at", "TIMESTAMP", "")],
    "order_items": [("order_id", "BIGINT", "PK/FK"), ("product_id", "BIGINT", "PK/FK"), ("quantity", "INTEGER", ""), ("ordered_price", "INTEGER", "")],
    "payments": [("payment_id", "BIGINT", "PK"), ("order_id", "BIGINT", "FK/UQ"), ("amount", "INTEGER", ""), ("payment_method", "VARCHAR", ""), ("status", "VARCHAR", ""), ("paid_at", "TIMESTAMP", ""), ("refunded_at", "TIMESTAMP", "")],
}

RELATIONS = [
    ("categories", "category_id", "products", "category_id", "1:N"),
    ("stores", "store_id", "inventories", "store_id", "1:N"),
    ("products", "product_id", "inventories", "product_id", "1:N"),
    ("users", "user_id", "carts", "user_id", "1:0..1"),
    ("stores", "store_id", "carts", "store_id", "1:N"),
    ("carts", "cart_id", "cart_items", "cart_id", "1:N"),
    ("products", "product_id", "cart_items", "product_id", "1:N"),
    ("users", "user_id", "orders", "user_id", "1:N"),
    ("stores", "store_id", "orders", "store_id", "1:N"),
    ("orders", "order_id", "order_items", "order_id", "1:N"),
    ("products", "product_id", "order_items", "product_id", "1:N"),
    ("orders", "order_id", "payments", "order_id", "1:1"),
]

POSITIONS = {
    "users": (50, 100), "carts": (50, 440), "cart_items": (500, 470),
    "categories": (960, 90), "products": (960, 350), "inventories": (1480, 370),
    "stores": (1940, 90), "orders": (380, 1050), "order_items": (980, 1080),
    "payments": (1550, 1090),
}


def canvas(title: str, size=(1800, 1050)):
    image = Image.new("RGB", size, "#F8FAFC")
    draw = ImageDraw.Draw(image)
    draw.rectangle((0, 0, size[0], 82), fill="#14532D")
    draw.text((36, 21), title, font=font(30, True), fill="white")
    return image, draw


def box(draw, xy, title, lines, width=370, accent="#166534"):
    x, y = xy
    height = 58 + len(lines) * 29
    draw.rounded_rectangle((x, y, x + width, y + height), 12, fill="white", outline="#94A3B8", width=2)
    draw.rounded_rectangle((x, y, x + width, y + 46), 12, fill=accent)
    draw.rectangle((x, y + 32, x + width, y + 46), fill=accent)
    draw.text((x + 14, y + 9), title, font=font(19, True), fill="white")
    for index, line in enumerate(lines):
        draw.text((x + 13, y + 54 + index * 29), line, font=font(15), fill="#1E293B")
    return x, y, x + width, y + height


def build_erd_png() -> None:
    image, draw = canvas("Where Is My Kimbap? 4.0 — Crow's Feet ERD", (2420, 1580))
    rects = {
        name: (POSITIONS[name][0], POSITIONS[name][1], POSITIONS[name][0] + 410,
               POSITIONS[name][1] + 58 + len(fields) * 29)
        for name, fields in TABLES.items()
    }
    for parent, _, child, _, cardinality in RELATIONS:
        parent_rect, child_rect = rects[parent], rects[child]
        pcenter = ((parent_rect[0] + parent_rect[2]) // 2, (parent_rect[1] + parent_rect[3]) // 2)
        ccenter = ((child_rect[0] + child_rect[2]) // 2, (child_rect[1] + child_rect[3]) // 2)
        if abs(ccenter[0] - pcenter[0]) >= abs(ccenter[1] - pcenter[1]):
            direction = 1 if ccenter[0] > pcenter[0] else -1
            start = (parent_rect[2] if direction == 1 else parent_rect[0], pcenter[1])
            end = (child_rect[0] if direction == 1 else child_rect[2], ccenter[1])
            draw.line((*start, *end), fill="#475569", width=3)
            draw.line((start[0] + 10 * direction, start[1] - 11, start[0] + 10 * direction, start[1] + 11), fill="#475569", width=3)
            if cardinality.endswith(":1"):
                draw.line((end[0] - 10 * direction, end[1] - 11, end[0] - 10 * direction, end[1] + 11), fill="#475569", width=3)
            else:
                for offset in (-13, 0, 13):
                    draw.line((end[0], end[1], end[0] - 18 * direction, end[1] + offset), fill="#475569", width=3)
        else:
            direction = 1 if ccenter[1] > pcenter[1] else -1
            start = (pcenter[0], parent_rect[3] if direction == 1 else parent_rect[1])
            end = (ccenter[0], child_rect[1] if direction == 1 else child_rect[3])
            draw.line((*start, *end), fill="#475569", width=3)
            draw.line((start[0] - 11, start[1] + 10 * direction, start[0] + 11, start[1] + 10 * direction), fill="#475569", width=3)
            if cardinality.endswith(":1"):
                draw.line((end[0] - 11, end[1] - 10 * direction, end[0] + 11, end[1] - 10 * direction), fill="#475569", width=3)
            else:
                for offset in (-13, 0, 13):
                    draw.line((end[0], end[1], end[0] + offset, end[1] - 18 * direction), fill="#475569", width=3)
        draw.text(((start[0] + end[0]) // 2 + 5, (start[1] + end[1]) // 2 - 23), cardinality, font=font(13, True), fill="#334155")
    # 관계선을 먼저 그린 뒤 테이블을 올려 선이 컬럼 텍스트를 가리지 않게 한다.
    for name, fields in TABLES.items():
        box(draw, POSITIONS[name], name, [f"{key:6} {column} : {dtype}" for column, dtype, key in fields], 410)
    output = ROOT / "docs" / "erd" / "where_is_my_kimbap_4.0_erd.png"
    image.save(output)


def build_erd_json() -> None:
    now = int(time.time() * 1000)
    tables, columns, relationships = {}, {}, {}
    name_to_id, column_lookup = {}, {}
    for table_index, (name, fields) in enumerate(TABLES.items(), 1):
        table_id = f"table-{table_index:02d}-{name}"
        name_to_id[name] = table_id
        column_ids = []
        for column_index, (column, data_type, key) in enumerate(fields, 1):
            column_id = f"column-{table_index:02d}-{column_index:02d}-{column}"
            column_ids.append(column_id)
            column_lookup[(name, column)] = column_id
            columns[column_id] = {
                "id": column_id, "tableId": table_id, "name": column, "comment": key,
                "dataType": data_type.lower(), "default": "", "options": 10 if key else 0,
                "ui": {"keys": 1 if "PK" in key else 3 if "FK" in key else 0, "widthName": 120, "widthComment": 60, "widthDataType": 80, "widthDefault": 60},
                "meta": {"updateAt": now, "createAt": now},
            }
        x, y = POSITIONS[name]
        tables[table_id] = {"id": table_id, "name": name, "comment": "", "columnIds": column_ids, "seqColumnIds": column_ids,
                            "ui": {"x": x, "y": y, "zIndex": table_index, "widthName": 160, "widthComment": 60, "color": ""},
                            "meta": {"updateAt": now, "createAt": now}}
    for index, (parent, pcolumn, child, ccolumn, _) in enumerate(RELATIONS, 1):
        relation_id = f"relationship-{index:02d}"
        px, py = POSITIONS[parent]
        cx, cy = POSITIONS[child]
        relationships[relation_id] = {
            "id": relation_id, "identification": "PK" in next(k for c, _, k in TABLES[child] if c == ccolumn),
            "relationshipType": 16, "startRelationshipType": 2,
            "start": {"tableId": name_to_id[parent], "columnIds": [column_lookup[(parent, pcolumn)]], "x": px + 410, "y": py + 70, "direction": 2},
            "end": {"tableId": name_to_id[child], "columnIds": [column_lookup[(child, ccolumn)]], "x": cx, "y": cy + 70, "direction": 1},
            "meta": {"updateAt": now, "createAt": now},
        }
    output = {
        "$schema": "https://raw.githubusercontent.com/dineug/erd-editor/main/json-schema/schema.json", "version": "3.0.0",
        "settings": {"width": 2500, "height": 1700, "scrollTop": 0, "scrollLeft": 0, "zoomLevel": 0.65, "show": 294,
                     "database": 16, "databaseName": "where_is_my_kimbap_4_0", "canvasType": "ERD", "language": 1,
                     "tableNameCase": 4, "columnNameCase": 2, "bracketType": 1, "relationshipDataTypeSync": True,
                     "relationshipOptimization": False, "columnOrder": [1, 2, 4, 8, 16, 32, 64], "maxWidthComment": -1, "ignoreSaveSettings": 0},
        "doc": {"tableIds": list(tables), "relationshipIds": list(relationships), "indexIds": [], "memoIds": []},
        "collections": {"tableEntities": tables, "tableColumnEntities": columns, "relationshipEntities": relationships,
                        "indexEntities": {}, "indexColumnEntities": {}, "memoEntities": {}},
    }
    (ROOT / "docs" / "erd" / "where_is_my_kimbap_4.0.erd.json").write_text(json.dumps(output, ensure_ascii=False, indent=2), encoding="utf-8")


def wireframe(filename: str, title: str, elements: list[tuple[str, tuple[int, int, int, int]]]) -> None:
    image, draw = canvas(f"구현 전 UI Wireframe — {title}", (1440, 900))
    draw.rectangle((25, 105, 230, 870), fill="#E2E8F0", outline="#64748B", width=2)
    menu = ["주변 매장", "매장 상품", "상품 비교", "장바구니", "주문 내역", "데이터 관리"]
    for index, label in enumerate(menu):
        fill = "#BBF7D0" if label == title else "#F1F5F9"
        draw.rounded_rectangle((45, 135 + index * 82, 210, 190 + index * 82), 8, fill=fill, outline="#94A3B8")
        draw.text((60, 151 + index * 82), label, font=font(17), fill="#1E293B")
    draw.text((270, 115), title, font=font(29, True), fill="#14532D")
    for label, bounds in elements:
        draw.rounded_rectangle(bounds, 9, fill="white", outline="#64748B", width=2)
        draw.text((bounds[0] + 12, bounds[1] + 11), label, font=font(17), fill="#334155")
    image.save(ROOT / "docs" / "ui_design" / filename)


def build_wireframes() -> None:
    wireframe("wireframe_login.png", "로그인", [("Where Is My Kimbap?", (470, 175, 1050, 260)), ("아이디", (470, 310, 1050, 375)), ("비밀번호", (470, 400, 1050, 465)), ("로그인", (470, 510, 1050, 575)), ("데모 계정 안내", (470, 610, 1050, 670))])
    wireframe("wireframe_nearby.png", "주변 매장", [("위도", (280, 175, 480, 235)), ("경도", (500, 175, 700, 235)), ("거리순 조회", (720, 175, 890, 235)), ("매장 이미지 / 이름 / 거리 / 주소", (280, 285, 1300, 440)), ("매장 이미지 / 이름 / 거리 / 주소", (280, 470, 1300, 625))])
    wireframe("wireframe_inventory.png", "매장 상품", [("편의점 Dropdown", (280, 175, 560, 235)), ("카테고리", (580, 175, 800, 235)), ("상품명 검색", (820, 175, 1110, 235)), ("이미지 | 상품 | 가격 | 재고 | 진열위치 | 담기", (280, 285, 1300, 740))])
    wireframe("wireframe_compare.png", "상품 비교", [("상품명 검색", (280, 175, 650, 235)), ("상품 | 매장 | 가격 | 재고 / 미등록 행 유지", (280, 285, 1300, 740))])
    wireframe("wireframe_cart.png", "장바구니", [("상품 | 단가 | 수량 - + | 삭제", (280, 175, 1300, 550)), ("합계", (280, 620, 520, 690)), ("결제 방법", (550, 620, 800, 690)), ("가상 결제", (830, 620, 1040, 690))])
    wireframe("wireframe_orders.png", "주문 내역", [("바코드 | 주문번호 | 매장 | 금액 | 상태 | 수령 완료", (280, 175, 1300, 390)), ("바코드 | 주문번호 | 매장 | 금액 | 상태", (280, 430, 1300, 645))])
    wireframe("wireframe_admin.png", "데이터 관리", [("카테고리 | 상품명 | 제조사 | 포장 단위 | 상품 추가", (280, 175, 1300, 285)), ("매장 ID | 상품 ID | 가격 | 재고 | 진열 위치", (280, 360, 1300, 470)), ("재고 저장 | 재고 삭제 | 상품 삭제", (280, 520, 950, 600))])


def diagram(path: Path, title: str, nodes: list[tuple[str, str, int, int, int]], edges: list[tuple[str, str, str]]) -> None:
    image, draw = canvas(title, (1700, 1000))
    rects = {key: box(draw, (x, y), label, [], width) for key, label, x, y, width in nodes}
    for start_key, end_key, label in edges:
        start_rect, end_rect = rects[start_key], rects[end_key]
        start = ((start_rect[0] + start_rect[2]) // 2, (start_rect[1] + start_rect[3]) // 2)
        end = ((end_rect[0] + end_rect[2]) // 2, (end_rect[1] + end_rect[3]) // 2)
        draw.line((*start, *end), fill="#475569", width=4)
        draw.text(((start[0] + end[0]) // 2 + 7, (start[1] + end[1]) // 2 - 25), label, font=font(15), fill="#1E293B")
    path.parent.mkdir(parents=True, exist_ok=True)
    image.save(path)


def build_other_diagrams() -> None:
    diagram(ROOT / "docs" / "architecture" / "system_architecture.png", "전체 시스템 구성도",
            [("user", "사용자", 680, 110, 300), ("view", "Flet Views", 640, 290, 380), ("service", "KimbapService", 640, 470, 380), ("repo", "Repositories", 640, 650, 380), ("db", "DuckDB 10 tables", 1160, 650, 360), ("asset", "assets/images", 1160, 300, 360)],
            [("user", "view", "입력/조회"), ("view", "service", "업무 요청"), ("service", "repo", "검증/호출"), ("repo", "db", "SQL"), ("view", "asset", "이미지/fallback")])
    diagram(ROOT / "docs" / "repository" / "repository_interface.png", "Repository Interface Diagram",
            [("view", "6 Flet Views", 650, 100, 400), ("service", "KimbapService", 650, 270, 400), ("user", "UserRepository", 60, 540, 300), ("store", "StoreRepository", 390, 540, 300), ("product", "ProductRepository", 720, 540, 320), ("cart", "CartRepository", 1070, 540, 300), ("order", "OrderRepository", 1400, 540, 280), ("db", "DuckDB", 690, 800, 400)],
            [("view", "service", "호출"), ("service", "user", "인증"), ("service", "store", "거리 검색"), ("service", "product", "JOIN/CRUD"), ("service", "cart", "수량 검증"), ("service", "order", "트랜잭션"), ("product", "db", "SQL"), ("order", "db", "SQL")])
    diagram(ROOT / "docs" / "use_case" / "use_case_diagram.png", "Use Case Diagram",
            [("actor", "사용자", 70, 420, 260), ("login", "로그인", 500, 100, 330), ("store", "주변 매장 조회", 500, 250, 330), ("stock", "상품·재고 조회", 500, 400, 330), ("cart", "장바구니 관리", 500, 550, 330), ("order", "주문·픽업", 500, 700, 330), ("admin", "관리자", 1350, 420, 260), ("crud", "상품·재고 CRUD", 980, 420, 330)],
            [("actor", "login", ""), ("actor", "store", ""), ("actor", "stock", ""), ("actor", "cart", ""), ("actor", "order", ""), ("admin", "crud", "")])

    image, draw = canvas("Sequence Diagram — 주문·결제·재고 차감", (1800, 1100))
    actors = [("사용자", 130), ("Flet View", 450), ("KimbapService", 780), ("OrderRepository", 1140), ("DuckDB", 1580)]
    for label, x in actors:
        draw.rounded_rectangle((x - 115, 110, x + 115, 165), 9, fill="#166534")
        draw.text((x - 95, 125), label, font=font(17, True), fill="white")
        draw.line((x, 165, x, 1030), fill="#94A3B8", width=2)
    messages = [(130, 450, 230, "가상 결제"), (450, 780, 320, "place_order"), (780, 1140, 410, "place_from_cart"), (1140, 1580, 500, "BEGIN / 장바구니 JOIN"), (1580, 1140, 600, "가격·재고 행"), (1140, 1580, 690, "orders/order_items/payments INSERT"), (1140, 1580, 780, "inventories UPDATE / COMMIT"), (1140, 780, 870, "order_id"), (780, 450, 950, "주문 완료"), (450, 130, 1020, "바코드 표시")]
    for x1, x2, y, label in messages:
        draw.line((x1, y, x2, y), fill="#334155", width=3)
        direction = 1 if x2 > x1 else -1
        draw.polygon([(x2, y), (x2 - 12 * direction, y - 7), (x2 - 12 * direction, y + 7)], fill="#334155")
        draw.text((min(x1, x2) + 15, y - 28), label, font=font(15), fill="#1E293B")
    image.save(ROOT / "docs" / "sequence" / "sequence_diagram.png")


def main() -> None:
    build_erd_json()
    build_erd_png()
    build_wireframes()
    build_other_diagrams()
    print("design assets generated")


if __name__ == "__main__":
    main()
