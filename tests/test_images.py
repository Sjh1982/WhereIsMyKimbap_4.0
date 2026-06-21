from app.services.image_service import ImageService


def test_existing_relative_image_is_resolved_for_flet_assets():
    assert ImageService().resolve("assets/images/default_store.png", "store") == "images/default_store.png"


def test_missing_and_unsafe_images_use_fallback():
    service = ImageService()
    assert service.resolve("missing.png") == "images/default_product.png"
    assert service.resolve("C:/private/image.png", "store") == "images/default_store.png"
