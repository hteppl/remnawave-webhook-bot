from typing import Dict, Any

from src.formatters.base import BaseEventFormatter
from src.i18n import get_translation as _


class UserEventFormatter(BaseEventFormatter):
    """Formatter for user-related events."""

    def format(self, event_type: str, data: Dict[str, Any], timestamp: str) -> str:
        """Format user event data."""
        event_name = self.get_event_name(event_type)

        # Get localized strings
        action_icon = _("message-header-action-icon")
        action_label = _("message-header-action-label")
        header_icon = _("event-user-header-icon")
        header_title = _("event-user-header-title")
        time_icon = _("message-header-time-icon")
        time_label = _("message-header-time-label")
        field_sep = _("message-separator-field")

        # Try to get event-specific icon
        event_icon_key = f"event-user-{event_name}-icon"
        event_icon = _(event_icon_key)
        if event_icon == event_icon_key:
            event_icon = action_icon

        # Get event message with parameters
        event_message_key = f"event-user-{event_name}-message"
        event_message = _(event_message_key, usage_percentage=data.get("usage_percentage", 0))

        # Build message
        msg = f"{event_icon} <b>{action_label}:</b> {event_message}\n\n"
        msg += f"<b>{header_icon} {header_title}</b>\n\n"
        msg += self._format_user_fields(data, field_sep)
        msg += f"\n{time_icon} <b>{time_label}:</b> {timestamp}"

        return msg

    def _format_user_fields(self, data: Dict[str, Any], field_sep: str) -> str:
        """Format user-specific fields."""
        msg = ""

        # Username
        if "username" in data:
            field_label = _("field-username")
            msg += self.format_field(field_sep, field_label, data["username"], use_code=True)

        # Email
        if "email" in data:
            field_label = _("field-email")
            msg += self.format_field(field_sep, field_label, data["email"])

        # Status
        if "status" in data:
            field_label = _("field-status")
            msg += self.format_field(field_sep, field_label, data["status"])

        # Data limit
        if "data_limit" in data:
            field_label = _("field-data-limit")
            msg += self.format_field(field_sep, field_label, data["data_limit"])

        # Expire
        if "expire" in data:
            field_label = _("field-expire")
            msg += self.format_field(field_sep, field_label, data["expire"])

        # Active squads
        if "activeInternalSquads" in data and data["activeInternalSquads"]:
            squads = ", ".join([squad["name"] for squad in data["activeInternalSquads"]])
            field_label = _("field-squads")
            msg += self.format_field(field_sep, field_label, squads, use_code=True)

        return msg
