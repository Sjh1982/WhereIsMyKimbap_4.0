from __future__ import annotations

import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.database import Database


@pytest.fixture
def database(tmp_path: Path) -> Database:
    db = Database(tmp_path / "test.duckdb")
    db.initialize(seed=True)
    return db
