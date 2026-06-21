"""Build deterministic DuckDB seed SQL from the reviewed 100-product catalog."""

from __future__ import annotations

import csv
import hashlib
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
CATALOG_PATH = ROOT / "docs" / "data" / "product_catalog_100.csv"
SEED_PATH = ROOT / "database" / "seed.sql"
CATALOG_MD_PATH = ROOT / "docs" / "data" / "product_catalog_100.md"

CATEGORIES = {
    "간편식": (1, 1, 3500),
    "컵라면": (2, 2, 1800),
    "과자": (3, 3, 1700),
    "음료": (4, 4, 1800),
    "유제품": (5, 5, 1900),
    "아이스크림": (6, 6, 1800),
    "생활용품": (7, 7, 3000),
}

STORES = [
    (1, "MA0106202201A1529897", "이마트24 금오공대 학생회관점", "이마트24", "경상북도 구미시 대학로 61 학생회관", 36.14566094, 128.3881288, True),
    (2, "MA0106202201A1529898", "이마트24 금오공대 기숙사점", "이마트24", "경상북도 구미시 대학로 61 기숙사", 36.14566094, 128.3881288, True),
    (3, "MA010120220808764145", "CU 금오공대 정문점", "CU", "경상북도 구미시 대학로 60", 36.14153931, 128.3961775, True),
    (4, "MA0101202309A0062091", "GS25 금오공대점", "GS25", "경상북도 구미시 대학로 39", 36.13931165, 128.396338, True),
    (5, "MA010120220812517210", "미니스톱 구미 금오공대점", "미니스톱", "경상북도 구미시 대학로 19", 36.13773286, 128.3972654, False),
]


def sql_text(value: str) -> str:
    return "'" + value.replace("'", "''") + "'"


def values_block(rows: list[str]) -> str:
    return ",\n    ".join(rows)


def load_catalog() -> list[dict[str, str]]:
    with CATALOG_PATH.open(encoding="utf-8-sig", newline="") as file:
        rows = list(csv.DictReader(file))
    if len(rows) != 100:
        raise ValueError(f"상품 카탈로그는 정확히 100행이어야 합니다: {len(rows)}")
    unknown = {row["category_name"] for row in rows} - CATEGORIES.keys()
    if unknown:
        raise ValueError(f"알 수 없는 카테고리: {sorted(unknown)}")
    return rows


def build_seed(products: list[dict[str, str]]) -> str:
    demo_hash = hashlib.sha256("1234".encode()).hexdigest()
    admin_hash = hashlib.sha256("admin1234".encode()).hexdigest()
    category_rows = [
        f"({category_id}, {sql_text(name)}, {order})"
        for name, (category_id, order, _) in CATEGORIES.items()
    ]
    store_rows = [
        "(" + ", ".join([
            str(store_id), sql_text(key), sql_text(name), sql_text(brand), sql_text(address),
            str(lat), str(lon), "NULL", sql_text("assets/images/default_store.png"),
            "TRUE" if active else "FALSE",
        ]) + ")"
        for store_id, key, name, brand, address, lat, lon, active in STORES
    ]
    product_rows: list[str] = []
    inventory_rows: list[str] = []
    for product_id, product in enumerate(products, start=1):
        category_id, _, base_price = CATEGORIES[product["category_name"]]
        limited = "TRUE" if product_id % 17 == 0 else "FALSE"
        product_rows.append(
            f"({product_id}, {category_id}, {sql_text(product['product_name'])}, "
            f"{sql_text(product['manufacturer'])}, {sql_text(product['package_size'])}, "
            f"'편의점 판매 후보 상품', 'assets/images/default_product.png', {limited})"
        )
        # 96~100번 상품은 의도적으로 재고 미등록 상태로 남겨 LEFT JOIN을 증명한다.
        if product_id > 95:
            continue
        for store_id, *_ in STORES:
            if (product_id + store_id * 7) % 3 == 0:
                continue
            price = base_price + (product_id % 5) * 100 + (store_id - 3) * 50
            stock = (product_id * 3 + store_id * 5) % 13
            shelf = f"{(product_id % 6) + 1}번 진열대 {'ABCD'[(product_id + store_id) % 4]}열"
            inventory_rows.append(
                f"({store_id}, {product_id}, {price}, {stock}, {sql_text(shelf)}, TIMESTAMP '2026-06-21 09:00:00')"
            )

    return f"""-- Where Is My Kimbap? 4.0 deterministic demo seed
-- 가격·재고·결제는 프로젝트용 예시이며 실제 POS/결제 데이터가 아니다.
BEGIN TRANSACTION;

INSERT INTO users VALUES
    (1, 'demo', '{demo_hash}', '데모 사용자', 'CUSTOMER', TIMESTAMP '2026-06-21 09:00:00'),
    (2, 'admin', '{admin_hash}', '관리자', 'ADMIN', TIMESTAMP '2026-06-21 09:00:00')
ON CONFLICT DO NOTHING;

INSERT INTO stores VALUES
    {values_block(store_rows)}
ON CONFLICT DO NOTHING;

INSERT INTO categories VALUES
    {values_block(category_rows)}
ON CONFLICT DO NOTHING;

INSERT INTO products VALUES
    {values_block(product_rows)}
ON CONFLICT DO NOTHING;

INSERT INTO inventories VALUES
    {values_block(inventory_rows)}
ON CONFLICT DO NOTHING;

INSERT INTO carts VALUES
    (1, 1, 3, TIMESTAMP '2026-06-21 10:00:00', TIMESTAMP '2026-06-21 10:00:00')
ON CONFLICT DO NOTHING;

INSERT INTO cart_items VALUES
    (1, 1, 1, TIMESTAMP '2026-06-21 10:01:00'),
    (1, 2, 2, TIMESTAMP '2026-06-21 10:02:00')
ON CONFLICT DO NOTHING;

INSERT INTO orders VALUES
    (1, 1, 4, 'A1B2C3D4', 'PICKED_UP', 7400, TIMESTAMP '2026-06-20 18:00:00', TIMESTAMP '2026-06-20 18:12:00', NULL)
ON CONFLICT DO NOTHING;

INSERT INTO order_items VALUES
    (1, 3, 1, 3550),
    (1, 4, 1, 3850)
ON CONFLICT DO NOTHING;

INSERT INTO payments VALUES
    (1, 1, 7400, 'CARD', 'PAID', TIMESTAMP '2026-06-20 18:00:00', NULL)
ON CONFLICT DO NOTHING;

COMMIT;
"""


def build_markdown(products: list[dict[str, str]]) -> str:
    lines = [
        "# 상품 카탈로그 100종",
        "",
        "상품명·제조사·포장 단위는 제출 전 공식 페이지에서 재확인해야 한다. 가격과 재고는 프로젝트 예시 데이터다.",
        "",
        "| ID | 카테고리 | 상품명 | 제조사 | 포장 단위 | 확인 메모 |",
        "|---:|---|---|---|---|---|",
    ]
    for index, row in enumerate(products, start=1):
        values = [str(index), row["category_name"], row["product_name"], row["manufacturer"], row["package_size"], row["verification_note"]]
        lines.append("| " + " | ".join(value.replace("|", "\\|") for value in values) + " |")
    return "\n".join(lines) + "\n"


def main() -> None:
    products = load_catalog()
    SEED_PATH.write_text(build_seed(products), encoding="utf-8")
    CATALOG_MD_PATH.write_text(build_markdown(products), encoding="utf-8")
    print(f"generated {SEED_PATH} ({len(products)} products)")


if __name__ == "__main__":
    main()
