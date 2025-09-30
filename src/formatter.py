from typing import Dict, Any

from src.i18n import get_translation as _


class MessageFormatter:
    """Format webhook data into readable Telegram messages."""

    @staticmethod
    def format_webhook_message(event_type: str, data: Dict[str, Any], timestamp: str) -> str:
        """
        Format webhook data into a readable Telegram message.

        Args:
            event_type: Event type (e.g., user.created, node.disabled)
            data: Event data dictionary
            timestamp: Event timestamp

        Returns:
            Formatted HTML message
        """
        # Build message header
        header_icon = _("message-header-icon")
        header_title = _("message-header-title")
        event_icon = _("message-header-event-icon")
        event_label = _("message-header-event-label")

        message = f"{header_icon} <b>{header_title}</b>\n\n"
        message += f"{event_icon} <b>{event_label}:</b> <code>{event_type}</code>\n"

        # Format based on event category
        if event_type.startswith('user.'):
            message += MessageFormatter._format_event(event_type, data, 'user', timestamp)
        elif event_type.startswith('node.'):
            message += MessageFormatter._format_event(event_type, data, 'node', timestamp)
        elif event_type.startswith('crm.'):
            message += MessageFormatter._format_event(event_type, data, 'crm', timestamp)
        elif event_type.startswith('service.'):
            message += MessageFormatter._format_event(event_type, data, 'service', timestamp)
        else:
            # Fallback for unknown events
            data_label = _("message-header-data-label")
            message += f"<b>{data_label}:</b>\n"
            message += f"<pre>{MessageFormatter._format_dict(data)}</pre>"

        return message

    @staticmethod
    def _format_event(event_type: str, data: Dict[str, Any], category: str, timestamp: str) -> str:
        """
        Format event message using i18n.

        Args:
            event_type: Full event type (e.g., user.created)
            data: Event data
            category: Event category (user, node, crm, service)
            timestamp: Event timestamp

        Returns:
            Formatted message section
        """
        # Extract event name from type (e.g., "created" from "user.created")
        event_parts = event_type.split('.')
        event_name = '-'.join(event_parts[1:]).replace('_', '-')  # Handle multi-part names and replace underscores

        # Get localized strings
        action_icon = _("message-header-action-icon")
        action_label = _("message-header-action-label")
        header_icon = _(f'event-{category}-header-icon')
        header_title = _(f'event-{category}-header-title')
        time_icon = _("message-header-time-icon")
        time_label = _("message-header-time-label")

        event_icon_key = f'event-{category}-{event_name}-icon'
        event_message_key = f'event-{category}-{event_name}-message'

        # Try to get event icon (optional)
        try:
            event_icon = _(event_icon_key)
            # Check if it's just the key returned (no translation found)
            if event_icon == event_icon_key:
                event_icon = "📌"
        except:
            event_icon = "📌"

        # Get event message with parameters
        event_message = _(
            event_message_key,
            usage_percentage=data.get('usage_percentage', 0)
        )

        field_sep = _('message-separator-field')

        # Build message
        msg = f"{event_icon} <b>{action_label}:</b> {event_message}\n\n"
        msg += f"<b>{header_icon} {header_title}</b>\n\n"

        # Add data fields
        msg += MessageFormatter._format_data_fields(data, field_sep)

        # Add timestamp at the end
        msg += f"\n{time_icon} <b>{time_label}:</b> {timestamp}"

        return msg

    @staticmethod
    def _format_data_fields(data: Dict[str, Any], field_sep: str) -> str:
        """Format data fields using i18n field labels."""
        msg = ""

        # Common fields mapping
        field_mapping = {
            'username': 'username',
            'email': 'email',
            'status': 'status',
            'data_limit': 'data-limit',
            'expire': 'expire',
            'name': 'name',
            'address': 'address',
            'ip': 'ip',
        }

        for data_key, i18n_key in field_mapping.items():
            if data_key in data:
                field_label = _(f'field-{i18n_key}')
                value = data[data_key]

                # Code formatting for sensitive fields
                if data_key in ['username', 'name', 'ip']:
                    msg += f"{field_sep}{field_label}: <code>{value}</code>\n"
                else:
                    msg += f"{field_sep}{field_label}: {value}\n"

        return msg

    @staticmethod
    def _format_dict(d: Dict[str, Any], indent: int = 0) -> str:
        """Format dictionary for display (fallback for unknown events)."""
        lines = []
        indent_str = '  ' * indent

        for key, value in d.items():
            if isinstance(value, dict):
                lines.append(f"{indent_str}{key}:")
                lines.append(MessageFormatter._format_dict(value, indent + 1))
            else:
                lines.append(f"{indent_str}{key}: {value}")

        return '\n'.join(lines)
