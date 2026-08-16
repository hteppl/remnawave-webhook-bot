import logging
from pathlib import Path
from typing import Callable

from fluent_compiler.bundle import FluentBundle

from src.config import config

logger = logging.getLogger(__name__)

FALLBACK_LANGUAGE = "en"
RESOURCE_NAME = "messages.ftl"


def setup_l10n() -> dict[str, Callable]:
    """
    Setup Fluent localization with compiled messages.

    FTL resources are compiled to Python functions once at startup and merged
    into a single flat table, so a lookup is one dict hit and one call, with no
    per-message locale fallback scan.

    Returns:
        Mapping of message key to its compiled formatting function
    """
    locales_dir = Path(config.LOCALES_DIR)

    messages: dict[str, Callable] = {}
    loaded = []
    # Fallback first so the configured language overrides it on collision.
    for locale in reversed(list(dict.fromkeys([config.LANGUAGE, FALLBACK_LANGUAGE]))):
        path = locales_dir / locale / RESOURCE_NAME
        if not path.is_file():
            continue

        bundle = FluentBundle.from_files(locale, [str(path)], use_isolating=False)
        for error in bundle.check_messages():
            logger.warning("Failed to compile message in %s: %s", path, error)

        messages.update(
            {key: fn for key, fn in bundle._compiled_messages.items() if not key.startswith("-") and "." not in key}
        )
        loaded.append(locale)

    if not messages:
        raise FileNotFoundError(f"No locale resources found in {locales_dir}")

    logger.info("Compiled %d messages from locales: %s", len(messages), ", ".join(reversed(loaded)))

    return messages


messages = setup_l10n()


def get_translation(key: str, **kwargs) -> str:
    """
    Get translation for a key.

    Args:
        key: Translation key
        **kwargs: Variables to pass to the translation

    Returns:
        Translated string, or the key itself if no locale defines it
    """
    message = messages.get(key)
    if message is None:
        return key

    errors = []
    value = message(kwargs, errors)
    for error in errors:
        logger.warning("Translation error for %s: %s", key, error)

    return value
