from src.formatters.base import BaseEventFormatter


class Formatter(BaseEventFormatter):
    async def format(self, event_type, data, timestamp, **kwargs):
        raise NotImplementedError


def test_generic_field_labels_are_html_escaped():
    msg = Formatter().format_generic_fields({"<b>evil</b>": "value"}, "- ")
    assert "<b>evil</b>" not in msg
    assert "&lt;b&gt;evil&lt;/b&gt;" in msg


def test_generic_field_values_are_html_escaped():
    msg = Formatter().format_generic_fields({"name": "<script>"}, "- ")
    assert "<script>" not in msg
    assert "&lt;script&gt;" in msg


def test_missing_icon_returns_empty_string():
    assert Formatter().get_event_icon("user.no_such_event") == ""
