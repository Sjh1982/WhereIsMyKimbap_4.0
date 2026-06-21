"""Build report evidence images for summary requirements 1 and 4."""
from pathlib import Path

import duckdb
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "docs" / "sql_results"
DB = ROOT / "database" / "where_is_my_kimbap.duckdb"
FONT = ImageFont.truetype(r"C:\Windows\Fonts\malgun.ttf", 19)
FONT_B = ImageFont.truetype(r"C:\Windows\Fonts\malgunbd.ttf", 23)
MONO = ImageFont.truetype(r"C:\Windows\Fonts\consola.ttf", 18)


def base(title: str, height: int = 1000):
    image = Image.new("RGB", (1700, height), "#F8FAFC")
    draw = ImageDraw.Draw(image)
    draw.rectangle((0, 0, 1700, 78), fill="#14532D")
    draw.text((28, 20), title, font=FONT_B, fill="white")
    return image, draw


def code_panel(draw, top: int, title: str, lines: list[str], height: int):
    draw.rounded_rectangle((25, top, 1675, top + height), 10, fill="#111827", outline="#334155")
    draw.text((45, top + 16), title, font=FONT_B, fill="#86EFAC")
    y = top + 58
    for line in lines:
        draw.text((45, y), line, font=MONO, fill="#F8FAFC")
        y += 27


def requirement_one():
    connection = duckdb.connect(str(DB), read_only=True)
    counts = {table: connection.execute(f"SELECT count(*) FROM {table}").fetchone()[0]
              for table in ("stores", "products", "inventories")}
    connection.close()
    image, draw = base("결과 요약 (1) — Entity 2개 + Relationship 1개 생성 및 데이터 삽입", 1120)
    ddl = [
        "CREATE TABLE IF NOT EXISTS stores (",
        "    store_id BIGINT PRIMARY KEY,",
        "    store_name VARCHAR NOT NULL UNIQUE, ...",
        ");",
        "CREATE TABLE IF NOT EXISTS products (",
        "    product_id BIGINT PRIMARY KEY,",
        "    category_id BIGINT NOT NULL REFERENCES categories(category_id), ...",
        ");",
        "CREATE TABLE IF NOT EXISTS inventories (",
        "    store_id BIGINT NOT NULL REFERENCES stores(store_id),",
        "    product_id BIGINT NOT NULL REFERENCES products(product_id),",
        "    selling_price INTEGER NOT NULL CHECK (selling_price >= 0),",
        "    stock_count INTEGER NOT NULL CHECK (stock_count >= 0),",
        "    PRIMARY KEY (store_id, product_id)",
        ");",
    ]
    code_panel(draw, 105, "database/schema.sql 발췌", ddl, 500)
    seed = [
        "INSERT INTO stores VALUES (...) ON CONFLICT DO NOTHING;",
        "INSERT INTO products VALUES (...) ON CONFLICT DO NOTHING;",
        "INSERT INTO inventories VALUES (...) ON CONFLICT DO NOTHING;",
    ]
    code_panel(draw, 630, "database/seed.sql 발췌", seed, 165)
    draw.rounded_rectangle((25, 825, 1675, 1065), 10, fill="white", outline="#94A3B8", width=2)
    draw.text((48, 850), "DuckDB 실제 삽입 결과", font=FONT_B, fill="#14532D")
    draw.text((70, 910), f"stores (Entity)       : {counts['stores']}행", font=FONT, fill="#1E293B")
    draw.text((570, 910), f"products (Entity)     : {counts['products']}행", font=FONT, fill="#1E293B")
    draw.text((1070, 910), f"inventories (Relationship) : {counts['inventories']}행", font=FONT, fill="#1E293B")
    draw.text((70, 975), "inventories가 stores와 products의 N:M 관계를 해소한다.", font=FONT, fill="#475569")
    image.save(OUT / "requirement_1_tables_and_seed.png")


def requirement_four():
    connection = duckdb.connect(str(DB), read_only=True)
    rows = connection.execute("""SELECT 'store' AS kind, store_name AS name, image_path FROM stores LIMIT 2
                               UNION ALL
                               SELECT 'product', product_name, image_path FROM products LIMIT 3""").fetchall()
    connection.close()
    image, draw = base("결과 요약 (4) — Image 상대경로 저장 및 Flet 출력", 940)
    sql = [
        "-- stores / products 테이블",
        "image_path VARCHAR NOT NULL CHECK (",
        "    length(trim(image_path)) > 0",
        "    AND image_path NOT LIKE '/%'",
        "    AND image_path NOT LIKE '\\\\%'",
        "    AND image_path NOT LIKE '%:%'",
        "),",
        "",
        "-- seed.sql",
        "'assets/images/default_store.png'",
        "'assets/images/default_product.png'",
    ]
    code_panel(draw, 105, "DuckDB SQL — 상대 이미지 경로만 허용", sql, 380)
    draw.rounded_rectangle((25, 515, 1675, 885), 10, fill="white", outline="#94A3B8", width=2)
    draw.text((48, 540), "DuckDB 저장값 조회 결과", font=FONT_B, fill="#14532D")
    headers = ("종류", "이름", "image_path")
    widths = (180, 650, 720)
    x = 55
    for index, header in enumerate(headers):
        draw.rectangle((x, 585, x + widths[index], 625), fill="#DCFCE7", outline="#94A3B8")
        draw.text((x + 8, 594), header, font=FONT_B, fill="#14532D")
        x += widths[index]
    for row_index, row in enumerate(rows):
        x, y = 55, 625 + row_index * 44
        for index, value in enumerate(row):
            draw.rectangle((x, y, x + widths[index], y + 44), fill="#F8FAFC" if row_index % 2 == 0 else "white", outline="#CBD5E1")
            draw.text((x + 8, y + 10), str(value), font=FONT, fill="#1E293B")
            x += widths[index]
    image.save(OUT / "requirement_4_image_storage.png")


if __name__ == "__main__":
    OUT.mkdir(parents=True, exist_ok=True)
    requirement_one()
    requirement_four()
    print("summary evidence generated")
