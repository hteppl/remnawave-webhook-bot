from typing import Any

from src.formatters.base import BaseEventFormatter


class ErrorsEventFormatter(BaseEventFormatter):
    """Formatter for `errors.*` events.

    Payload carries a single `description` field; anything else a newer panel adds is
    appended generically.
    """

    async def format(self, event_type: str, data: dict[str, Any], timestamp: str, **kwargs) -> str:
        t = self.get_common_translations()
        field_sep = t["field_sep"]

        msg = self._format_fields(data, field_sep, [("description", "field-description", False)])
        msg += self.format_generic_fields(data, field_sep, skip_keys={"description"})

        return self.build_standard_message(
            event_type=event_type,
            timestamp=timestamp,
            fields_content=msg,
        )
