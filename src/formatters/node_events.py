from typing import Dict, Any

from src.formatters.base import BaseEventFormatter
from src.i18n import get_translation as _


class NodeEventFormatter(BaseEventFormatter):
    """Formatter for node-related events."""

    async def format(self, event_type: str, data: Dict[str, Any], timestamp: str) -> str:
        """Format node event data."""
        event_name = self.get_event_name(event_type)

        # Get localized strings
        action_icon = _("message-header-action-icon")
        action_label = _("message-header-action-label")
        header_icon = _("event-node-header-icon")
        header_title = _("event-node-header-title")
        time_icon = _("message-header-time-icon")
        time_label = _("message-header-time-label")
        field_sep = _("message-separator-field")

        # Try to get event-specific icon
        event_icon_key = f"event-node-{event_name}-icon"
        event_icon = _(event_icon_key)
        if event_icon == event_icon_key:
            event_icon = action_icon

        # Get event message
        event_message_key = f"event-node-{event_name}-message"
        event_message = _(event_message_key)

        # Build message
        msg = f"{event_icon} <b>{action_label}:</b> {event_message}\n\n"
        msg += f"<b>{header_icon} {header_title}</b>\n\n"

        # Use special formatting for node.created
        if event_type == "node.created":
            msg += self._format_node_created_fields(data, field_sep)
        else:
            msg += self._format_node_fields(data, field_sep)

        msg += f"\n{time_icon} <b>{time_label}:</b> {timestamp}"

        return msg

    def _format_node_created_fields(self, data: Dict[str, Any], field_sep: str) -> str:
        """Format fields specifically for node.created event."""
        msg = ""

        # Node Name
        if "name" in data:
            field_label = _("field-node-name") if _("field-node-name") != "field-node-name" else "Node Name"
            msg += self.format_field(field_sep, field_label, data["name"], use_code=True)

        # Address (combine address and port)
        if "address" in data:
            field_label = _("field-address")
            address = data["address"]
            if "port" in data:
                address = f"{address}:{data['port']}"
            msg += self.format_field(field_sep, field_label, address)

        # Location (from country code)
        if "countryCode" in data:
            field_label = _("field-location") if _("field-location") != "field-location" else "Location"
            msg += self.format_field(field_sep, field_label, data["countryCode"])

        # Provider
        if "provider" in data and isinstance(data["provider"], dict) and "name" in data["provider"]:
            field_label = _("field-provider") if _("field-provider") != "field-provider" else "Provider"
            msg += self.format_field(field_sep, field_label, data["provider"]["name"], use_code=True)

        # Inbound information
        if "activeInbounds" in data and data["activeInbounds"]:
            inbound = data["activeInbounds"][0]  # Get first inbound
            field_label = _("field-inbound") if _("field-inbound") != "field-inbound" else "Inbound"

            # Extract protocol, security, and port
            protocol = inbound.get("type", "").upper()
            security = inbound.get("security", "")
            port = inbound.get("port", "")

            inbound_info = f"{protocol} protocol"
            if security:
                inbound_info += f" with {security.capitalize()} security"
            if port:
                inbound_info += f" on port {port}"

            msg += self.format_field(field_sep, field_label, inbound_info)

        return msg

    def _format_node_fields(self, data: Dict[str, Any], field_sep: str) -> str:
        """Format standard node fields for other node events."""
        msg = ""

        # Name
        if "name" in data:
            field_label = _("field-name")
            msg += self.format_field(field_sep, field_label, data["name"], use_code=True)

        # Address
        if "address" in data:
            field_label = _("field-address")
            msg += self.format_field(field_sep, field_label, data["address"])

        # Status
        if "status" in data:
            field_label = _("field-status")
            msg += self.format_field(field_sep, field_label, data["status"])

        # Last Status Message
        if "lastStatusMessage" in data:
            field_label = _("field-last-status-message")
            msg += self.format_field(field_sep, field_label, data["lastStatusMessage"])

        # Description
        if "description" in data:
            field_label = _("field-description")
            msg += self.format_field(field_sep, field_label, data["description"])

        return msg
