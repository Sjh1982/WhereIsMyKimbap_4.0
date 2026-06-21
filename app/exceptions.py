class AppError(Exception):
    """사용자에게 안전하게 표시할 수 있는 애플리케이션 오류."""


class DatabaseOperationError(AppError):
    """Repository가 DuckDB 오류를 의미 있는 문맥과 함께 변환한 예외."""


class ValidationError(AppError):
    """입력값 또는 비즈니스 규칙 위반."""


class NotFoundError(AppError):
    """요청한 엔터티를 찾지 못함."""


class InsufficientStockError(AppError):
    """주문 수량보다 현재 재고가 적음."""
