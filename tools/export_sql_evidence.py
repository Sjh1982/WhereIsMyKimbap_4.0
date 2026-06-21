"""Execute report JOIN queries and export searchable CSV plus PNG evidence."""
from __future__ import annotations

import csv
from pathlib import Path

import duckdb
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent.parent
DATABASE = ROOT / "database" / "where_is_my_kimbap.duckdb"
QUERY_DIR = ROOT / "database" / "queries"
OUTPUT_DIR = ROOT / "docs" / "sql_results"
FONT = ImageFont.truetype(r"C:\Windows\Fonts\malgun.ttf", 17)
FONT_BOLD = ImageFont.truetype(r"C:\Windows\Fonts\malgunbd.ttf", 19)
PARAMETERS = {
    "join_1_store_products": [3],
    "join_2_product_store_comparison": ["%"],
    "join_3_order_details": [1],
}


def export(query_path: Path) -> int:
    connection = duckdb.connect(str(DATABASE), read_only=True)
    cursor = connection.execute(query_path.read_text(encoding="utf-8"), PARAMETERS[query_path.stem])
    headers = [column[0] for column in cursor.description]
    rows = cursor.fetchall()
    connection.close()

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    with (OUTPUT_DIR / f"{query_path.stem}.csv").open("w", encoding="utf-8-sig", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(headers)
        writer.writerows(rows)

    if query_path.stem == "join_2_product_store_comparison":
        # LEFT JOIN의 핵심 증거인 미취급(NULL) 행을 캡처 상단에 배치한다.
        shown = ([row for row in rows if row[3] is None] + [row for row in rows if row[3] is not None])[:12]
    else:
        shown = rows[:12]
    widths = [
        max(135, min(340, int(max(
            [FONT_BOLD.getlength(str(header))] +
            [FONT.getlength("NULL" if row[index] is None else str(row[index])) for row in shown]
        ) + 24)))
        for index, header in enumerate(headers)
    ]
    total_width = sum(widths) + 40
    height = 150 + 43 * (len(shown) + 1)
    image = Image.new("RGB", (total_width, height), "white")
    draw = ImageDraw.Draw(image)
    draw.rectangle((0, 0, total_width, 75), fill="#14532D")
    draw.text((20, 18), query_path.stem, font=FONT_BOLD, fill="white")
    x = 20
    for index, header in enumerate(headers):
        draw.rectangle((x, 88, x + widths[index], 130), fill="#DCFCE7", outline="#64748B")
        draw.text((x + 7, 98), header, font=FONT_BOLD, fill="#14532D")
        x += widths[index]
    for row_index, row in enumerate(shown):
        x = 20
        y = 130 + row_index * 43
        for column_index, value in enumerate(row):
            text = "NULL" if value is None else str(value)
            if len(text) > 25:
                text = text[:23] + "…"
            draw.rectangle((x, y, x + widths[column_index], y + 43), fill="#F8FAFC" if row_index % 2 == 0 else "white", outline="#CBD5E1")
            draw.text((x + 7, y + 10), text, font=FONT, fill="#1E293B")
            x += widths[column_index]
    draw.text((20, height - 35), f"전체 {len(rows)}행 중 {len(shown)}행 표시 · 전체 결과는 같은 이름의 CSV 참조", font=FONT, fill="#475569")
    image.save(OUTPUT_DIR / f"{query_path.stem}.png")
    return len(rows)


def main() -> None:
    for path in sorted(QUERY_DIR.glob("join_*.sql")):
        print(path.stem, export(path))


if __name__ == "__main__":
    main()
