import logging
from pathlib import Path

from fluent.syntax import FluentParser, ast
from fluent_compiler.bundle import FluentBundle

from src.config import config

logger = logging.getLogger(__name__)

FALLBACK_LANGUAGE = "en"
RESOURCE_NAME = "messages.ftl"

_messages: dict[str, FluentBundle] = {}
_reported: set[str] = set()


def _message_ids(path: Path) -> list[str]:
    """
    Parse an FTL file and return its message ids (terms and attributes excluded).

    Args:
        path: Path to the FTL resource

    Returns:
        List of message ids defined by the resource
    """
    resource = FluentParser().parse(path.read_text(encoding="utf-8"))
    return [entry.id.name for entry in resource.body if isinstance(entry, ast.Message)]


def setup_l10n() -> dict[str, FluentBundle]:
    """
    Setup Fluent localization with compiled messages.

    FTL resources are compiled to Python functions once at startup and merged
    into a single flat table. Call this after logging is configured so compile
    diagnostics are actually emitted.

    Returns:
        Mapping of message key to the bundle that defines it
    """
    locales_dir = Path(config.LOCALES_DIR)

    messages: dict[str, FluentBundle] = {}
    loaded = []
    # Fallback first so the configured language overrides it on collision.
    for locale in reversed(list(dict.fromkeys([config.LANGUAGE, FALLBACK_LANGUAGE]))):
        path = locales_dir / locale / RESOURCE_NAME
        if not path.is_file():
            logger.warning("No locale resource for language %r at %s, skipping", locale, path)
            continue

        bundle = FluentBundle.from_files(locale, [str(path)], use_isolating=False)
        for error in bundle.check_messages():
            logger.warning("Failed to compile message in %s: %s", path, error)

        messages.update({key: bundle for key in _message_ids(path) if bundle.has_message(key)})
        loaded.append(locale)

    if not messages:
        raise FileNotFoundError(f"No locale resources found in {locales_dir}")

    logger.info("Compiled %d messages from locales: %s", len(messages), ", ".join(reversed(loaded)))

    _messages.clear()
    _messages.update(messages)
    _reported.clear()

    return messages


def _warn_once(key: str, msg: str, *args) -> None:
    if key in _reported:
        return
    _reported.add(key)
    logger.warning(msg, *args)


def has_translation(key: str) -> bool:
    """
    Check whether any loaded locale defines a key.

    Use this for optional messages, so probing for one does not log a warning.

    Args:
        key: Translation key

    Returns:
        True if the key is defined
    """
    if not _messages:
        setup_l10n()
    return key in _messages


def get_translation(key: str, **kwargs) -> str:
    """
    Get translation for a key.

    Args:
        key: Translation key
        **kwargs: Variables to pass to the translation

    Returns:
        Translated string, or the key itself if no locale defines it
    """
    if not _messages:
        setup_l10n()

    bundle = _messages.get(key)
    if bundle is None:
        _warn_once(key, "No translation defined for %s, using the key as-is", key)
        return key

    value, errors = bundle.format(key, kwargs)
    for error in errors:
        _warn_once(f"{key}!{type(error).__name__}", "Translation error for %s: %s", key, error)

    return value
