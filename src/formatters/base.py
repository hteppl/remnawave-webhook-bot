from abc import ABC, abstractmethod
from html import escape
from typing import Dict, Any

from src.i18n import get_translation as _


class BaseEventFormatter(ABC):
    """Base class for event formatters."""

    @abstractmethod
    async def format(self, event_type: str, data: Dict[str, Any], timestamp: str, **kwargs) -> str:
        """
        Format the event data into a message.

        Args:
            event_type: Full event type (e.g., user.created)
            data: Event data
            timestamp: Event timestamp
            **kwargs: Additional formatter-specific arguments

        Returns:
            Formatted message string
        """
        pass

    @staticmethod
    def get_event_name(event_type: str) -> str:
        """Extract event name from type (e.g., "created" from "user.created")."""
        event_parts = event_type.split(".")
        return "-".join(event_parts[1:]).replace("_", "-")

    @staticmethod
    def get_event_category(event_type: str) -> str:
        """Extract event category from type (e.g., "user" from "user.created")."""
        return event_type.split(".")[0]

    @staticmethod
    def escape_value(value: Any) -> str:
        """Escape HTML entities to prevent parsing errors."""
        return escape(str(value))

    def format_field(self, field_sep: str, field_label: str, value: Any, use_code: bool = False) -> str:
        """Format a single field with label and value."""
        escaped_value = self.escape_value(value)
        if use_code:
            return f"{field_sep}{field_label}: <code>{escaped_value}</code>\n"
        else:
            return f"{field_sep}{field_label}: {escaped_value}\n"

    def get_common_translations(self) -> Dict[str, str]:
        """Get common translation strings used across all formatters."""
        return {
            "action_icon": _("message-header-action-icon"),
            "action_label": _("message-header-action-label"),
            "time_icon": _("message-header-time-icon"),
            "time_label": _("message-header-time-label"),
            "field_sep": _("message-separator-field"),
        }

    def get_event_icon(self, event_type: str, fallback_icon: str = None) -> str:
        """
        Get event-specific icon with fallback.

        Args:
            event_type: Full event type (e.g., user.created)
            fallback_icon: Icon to use if specific icon not found

        Returns:
            Icon string
        """
        category = self.get_event_category(event_type)
        event_name = self.get_event_name(event_type)
        event_icon_key = f"event-{category}-{event_name}-icon"
        event_icon = _(event_icon_key)

        # If translation key not found, use fallback
        if event_icon == event_icon_key:
            return fallback_icon or _("message-header-action-icon")

        return event_icon

    def get_event_message(self, event_type: str, **kwargs) -> str:
        """
        Get event-specific message.

        Args:
            event_type: Full event type (e.g., user.created)
            **kwargs: Variables to pass to translation

        Returns:
            Message string
        """
        category = self.get_event_category(event_type)
        event_name = self.get_event_name(event_type)
        event_message_key = f"event-{category}-{event_name}-message"
        return _(event_message_key, **kwargs) if kwargs else _(event_message_key)

    def get_category_header(self, event_type: str) -> Dict[str, str]:
        """
        Get category-specific header icon and title.

        Args:
            event_type: Full event type

        Returns:
            Dictionary with 'icon' and 'title' keys
        """
        category = self.get_event_category(event_type)
        return {
            "icon": _(f"event-{category}-header-icon"),
            "title": _(f"event-{category}-header-title"),
        }

    def build_standard_message(
            self,
            event_type: str,
            timestamp: str,
            fields_content: str,
            additional_content: str = None,
            event_message_kwargs: Dict[str, Any] = None,
    ) -> str:
        """
        Build a standard formatted message.

        Args:
            event_type: Full event type
            timestamp: Event timestamp
            fields_content: Formatted fields content
            additional_content: Optional additional content to append
            event_message_kwargs: Optional kwargs for event message translation

        Returns:
            Formatted message string
        """
        translations = self.get_common_translations()
        header = self.get_category_header(event_type)
        event_icon = self.get_event_icon(event_type)
        event_message = self.get_event_message(event_type, **(event_message_kwargs or {}))

        # Build message
        msg = f"{event_icon} <b>{translations['action_label']}:</b> {event_message}\n\n"
        msg += f"<b>{header['icon']} {header['title']}</b>\n\n"
        msg += fields_content
        msg += f"\n{translations['time_icon']} <b>{translations['time_label']}:</b> {timestamp}"

        # Add additional content if provided
        if additional_content:
            msg += f"\n{additional_content}"

        return msg
