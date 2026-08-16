import importlib
import logging
from pathlib import Path

import pytest

LOCALES_DIR = Path(__file__).parent.parent / "locales"
LOCALES = sorted(p.name for p in LOCALES_DIR.iterdir() if (p / "messages.ftl").is_file())


@pytest.fixture
def l10n(monkeypatch):
    """Reload src.l10n with a given LANGUAGE, since config reads env at import."""

    def _load(language="en"):
        monkeypatch.setenv("LANGUAGE", language)
        import src.config

        importlib.reload(src.config)
        import src.l10n

        importlib.reload(src.l10n)
        src.l10n.setup_l10n()
        return src.l10n

    return _load


def test_all_locales_compile_without_errors(l10n):
    for locale in LOCALES:
        mod = l10n(locale)
        assert mod.get_translation("message-header-action") != "message-header-action"


def test_locales_have_identical_key_sets(l10n):
    key_sets = {locale: set(l10n(locale).setup_l10n()) for locale in LOCALES}
    reference = key_sets[l10n().FALLBACK_LANGUAGE]
    for locale, keys in key_sets.items():
        assert keys == reference, f"{locale} differs from fallback: {keys ^ reference}"


def test_terms_and_attributes_are_excluded(l10n):
    keys = l10n().setup_l10n()
    assert not [k for k in keys if k.startswith("-") or "." in k]


def test_configured_language_overrides_fallback(l10n):
    if "ru" not in LOCALES:
        pytest.skip("no ru locale")
    assert l10n("ru").get_translation("message-header-action") != l10n("en").get_translation("message-header-action")


def test_unknown_language_falls_back_and_warns(l10n, caplog):
    with caplog.at_level(logging.WARNING):
        mod = l10n("zz")
    assert "zz" in caplog.text
    assert mod.get_translation("message-header-action") == l10n("en").get_translation("message-header-action")


def test_missing_key_echoes_and_warns_once(l10n, caplog):
    mod = l10n()
    with caplog.at_level(logging.WARNING):
        # The key echo is a load-bearing sentinel for optional messages.
        assert mod.get_translation("no-such-key") == "no-such-key"
        assert mod.get_translation("no-such-key") == "no-such-key"
    assert caplog.text.count("no-such-key") == 1


def test_has_translation_does_not_warn(l10n, caplog):
    mod = l10n()
    with caplog.at_level(logging.WARNING):
        assert mod.has_translation("message-header-action")
        assert not mod.has_translation("no-such-key")
    assert caplog.text == ""


def test_use_isolating_is_off(l10n):
    # Fluent's bidi isolation chars would corrupt Telegram HTML output.
    value = l10n().get_translation("topic-startup-message", topic_name="TOPIC_USER")
    assert "⁨" not in value and "⁩" not in value
    assert "TOPIC_USER" in value


def test_translation_error_warns_once(l10n, caplog):
    mod = l10n()
    with caplog.at_level(logging.WARNING):
        mod.get_translation("topic-startup-message")
        mod.get_translation("topic-startup-message")
    assert caplog.text.count("Translation error") == 1
