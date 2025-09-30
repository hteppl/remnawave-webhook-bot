from typing import Dict, Any

from src.formatters.base import BaseEventFormatter
from src.i18n import get_translation as _


class ServiceEventFormatter(BaseEventFormatter):
    """Formatter for service-related events."""

    def format(self, event_type: str, data: Dict[str, Any], timestamp: str) -> str:
        """Format service event data."""
        event_name = self.get_event_name(event_type)

        # Get localized strings
        action_icon = _("message-header-action-icon")
        action_label = _("message-header-action-label")
        time_icon = _("message-header-time-icon")
        time_label = _("message-header-time-label")
        field_sep = _("message-separator-field")

        # Try to get event-specific icon
        event_icon_key = f"event-service-{event_name}-icon"
        event_icon = _(event_icon_key)
        if event_icon == event_icon_key:
            event_icon = action_icon

        # Get event message
        event_message_key = f"event-service-{event_name}-message"
        event_message = _(event_message_key)

        # Build message
        msg = f"{event_icon} <b>{action_label}:</b> {event_message}\n\n"

        # Only show data for specific service events
        show_data = event_type in ["service.login_attempt_failed", "service.login_attempt_success"]

        if show_data:
            msg += self._format_service_fields(data, field_sep)
            msg += "\n"

        msg += f"{time_icon} <b>{time_label}:</b> {timestamp}"

        return msg

    def _format_service_fields(self, data: Dict[str, Any], field_sep: str) -> str:
        """Format service-specific fields."""
        msg = ""

        # Flatten nested objects (e.g., loginAttempt)
        flattened_data = {}
        for key, value in data.items():
            if isinstance(value, dict):
                flattened_data.update(value)
            else:
                flattened_data[key] = value

        # IP Address
        if "ip" in flattened_data:
            field_label = _("field-ip")
            msg += self.format_field(field_sep, field_label, flattened_data["ip"], use_code=True)

        # User Agent
        if "userAgent" in flattened_data:
            field_label = _("field-user-agent")
            msg += self.format_field(field_sep, field_label, flattened_data["userAgent"])

        # Username (for login attempts)
        if "username" in flattened_data:
            field_label = _("field-username")
            msg += self.format_field(field_sep, field_label, flattened_data["username"], use_code=True)

        # Password (if shown in failed login attempts)
        if "password" in flattened_data:
            field_label = _("field-password")
            msg += self.format_field(field_sep, field_label, flattened_data["password"], use_code=True)

        return msg
