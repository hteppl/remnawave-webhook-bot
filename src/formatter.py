from typing import Dict, Any

from src.formatters import UserEventFormatter, NodeEventFormatter, CRMEventFormatter, ServiceEventFormatter
from src.i18n import get_translation as _


class MessageFormatter:
    """Format webhook data into readable Telegram messages."""

    def __init__(self):
        self.user_formatter = UserEventFormatter()
        self.node_formatter = NodeEventFormatter()
        self.crm_formatter = CRMEventFormatter()
        self.service_formatter = ServiceEventFormatter()

    async def format_webhook_message(self, event_type: str, data: Dict[str, Any], timestamp: str) -> str:
        """
        Format webhook data into a readable Telegram message.

        Args:
            event_type: Event type (e.g., user.created, node.disabled)
            data: Event data dictionary
            timestamp: Event timestamp

        Returns:
            Formatted HTML message
        """
        # Format based on event category
        if event_type.startswith("user."):
            return await self.user_formatter.format(event_type, data, timestamp)
        elif event_type.startswith("node."):
            return await self.node_formatter.format(event_type, data, timestamp)
        elif event_type.startswith("crm."):
            return await self.crm_formatter.format(event_type, data, timestamp)
        elif event_type.startswith("service."):
            return await self.service_formatter.format(event_type, data, timestamp)
        else:
            # Fallback for unknown events
            event_icon = _("message-header-event-icon")
            event_label = _("message-header-event-label")
            data_label = _("message-header-data-label")

            message = f"{event_icon} <b>{event_label}:</b> <code>{event_type}</code>\n"
            message += f"<b>{data_label}:</b>\n"
            message += f"<pre>{self._format_dict(data)}</pre>"
            return message

    @staticmethod
    def _format_dict(d: Dict[str, Any], indent: int = 0) -> str:
        """Format dictionary for display (fallback for unknown events)."""
        lines = []
        indent_str = "  " * indent

        for key, value in d.items():
            if isinstance(value, dict):
                lines.append(f"{indent_str}{key}:")
                lines.append(MessageFormatter._format_dict(value, indent + 1))
            else:
                lines.append(f"{indent_str}{key}: {value}")

        return "\n".join(lines)
