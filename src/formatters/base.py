from abc import ABC, abstractmethod
from html import escape
from typing import Dict, Any


class BaseEventFormatter(ABC):
    """Base class for event formatters."""

    @abstractmethod
    async def format(self, event_type: str, data: Dict[str, Any], timestamp: str) -> str:
        """
        Format the event data into a message.

        Args:
            event_type: Full event type (e.g., user.created)
            data: Event data
            timestamp: Event timestamp

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
