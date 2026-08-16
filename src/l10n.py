from pathlib import Path

from fluent.runtime import FluentLocalization, FluentResourceLoader

from src.config import config


def setup_i18n() -> FluentLocalization:
    """
    Setup Fluent localization directly without aiogram middleware.

    Returns:
        FluentLocalization instance
    """
    locales_dir = Path(config.LOCALES_DIR)

    loader = FluentResourceLoader(str(locales_dir / "{locale}"))

    return FluentLocalization([config.LANGUAGE], ["messages.ftl"], loader)


i18n = setup_i18n()


def get_translation(key: str, **kwargs) -> str:
    """
    Get translation for a key.

    Args:
        key: Translation key
        **kwargs: Variables to pass to the translation

    Returns:
        Translated string
    """
    return i18n.format_value(key, kwargs) if kwargs else i18n.format_value(key)
