from __future__ import annotations

import hashlib

import duckdb

from app.database import Database
from app.exceptions import DatabaseOperationError


class UserRepository:
    def __init__(self, database: Database) -> None:
        self.database = database

    def authenticate(self, login_id: str, password: str) -> dict | None:
        password_hash = hashlib.sha256(password.encode()).hexdigest()
        try:
            with self.database.connection() as connection:
                row = connection.execute(
                    """SELECT user_id, login_id, user_name, role
                       FROM users WHERE login_id = ? AND password_hash = ?""",
                    [login_id.strip(), password_hash],
                ).fetchone()
            if row is None:
                return None
            return dict(zip(("user_id", "login_id", "user_name", "role"), row))
        except duckdb.Error as exc:
            print(f"[DuckDB] 사용자 인증 실패: {exc}")
            raise DatabaseOperationError("로그인 정보를 확인하지 못했습니다.") from exc
