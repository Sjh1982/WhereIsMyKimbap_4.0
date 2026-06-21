from __future__ import annotations

from contextlib import contextmanager
from pathlib import Path
from typing import Iterator

import duckdb

from app.config import DATABASE_PATH, SCHEMA_PATH, SEED_PATH
from app.exceptions import DatabaseOperationError


class Database:
    def __init__(self, path: Path | str = DATABASE_PATH) -> None:
        self.path = Path(path) if str(path) != ":memory:" else Path(":memory:")

    def connect(self) -> duckdb.DuckDBPyConnection:
        if str(self.path) != ":memory:":
            self.path.parent.mkdir(parents=True, exist_ok=True)
        return duckdb.connect(str(self.path))

    def initialize(self, seed: bool = True) -> None:
        try:
            with self.connection() as connection:
                connection.execute(SCHEMA_PATH.read_text(encoding="utf-8"))
                if seed and SEED_PATH.exists():
                    connection.execute(SEED_PATH.read_text(encoding="utf-8"))
        except (OSError, duckdb.Error) as exc:
            print(f"[DuckDB] 초기화 실패: {exc}")
            raise DatabaseOperationError("데이터베이스를 초기화하지 못했습니다.") from exc

    @contextmanager
    def connection(self) -> Iterator[duckdb.DuckDBPyConnection]:
        connection = self.connect()
        try:
            yield connection
        finally:
            connection.close()

    @contextmanager
    def transaction(self) -> Iterator[duckdb.DuckDBPyConnection]:
        with self.connection() as connection:
            connection.execute("BEGIN TRANSACTION")
            try:
                yield connection
                connection.execute("COMMIT")
            except Exception:
                connection.execute("ROLLBACK")
                raise
