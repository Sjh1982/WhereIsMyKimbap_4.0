from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATABASE_DIR = PROJECT_ROOT / "database"
DATABASE_PATH = DATABASE_DIR / "where_is_my_kimbap.duckdb"
SCHEMA_PATH = DATABASE_DIR / "schema.sql"
SEED_PATH = DATABASE_DIR / "seed.sql"
ASSETS_DIR = PROJECT_ROOT / "assets"
DEFAULT_STORE_IMAGE = "assets/images/default_store.png"
DEFAULT_PRODUCT_IMAGE = "assets/images/default_product.png"

# 금오공과대학교 중심 좌표. 사용자가 직접 좌표를 입력하지 않았을 때만 사용한다.
DEFAULT_LATITUDE = 36.1456
DEFAULT_LONGITUDE = 128.3935
