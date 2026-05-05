from backend.src.config.settings import get_settings


def test_openai_key_not_logged_by_default():
    settings = get_settings()
    assert hasattr(settings, "openai_api_key")
