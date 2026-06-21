from pathlib import Path

from app.config import DEFAULT_PRODUCT_IMAGE, DEFAULT_STORE_IMAGE, PROJECT_ROOT


class ImageService:
    """DB 상대경로를 검증하고 Flet assets 경로로 변환한다."""

    def resolve(self, image_path: str | None, kind: str = "product") -> str:
        fallback = DEFAULT_STORE_IMAGE if kind == "store" else DEFAULT_PRODUCT_IMAGE
        candidate = image_path or fallback
        path = Path(candidate)
        if path.is_absolute() or ":" in candidate:
            candidate = fallback
        absolute = (PROJECT_ROOT / candidate).resolve()
        try:
            absolute.relative_to(PROJECT_ROOT)
        except ValueError:
            absolute = (PROJECT_ROOT / fallback).resolve()
        if not absolute.is_file():
            absolute = (PROJECT_ROOT / fallback).resolve()
        return absolute.relative_to(PROJECT_ROOT / "assets").as_posix()
