from typing import Dict, Any

from src.formatters.base import BaseEventFormatter
from src.i18n import get_translation as _


class NodeEventFormatter(BaseEventFormatter):
    """Formatter for node-related events."""

    async def format(
        self, event_type: str, data: Dict[str, Any], timestamp: str, connection_stats: str = None, **kwargs
    ) -> str:
        """Format node event data."""
        translations = self.get_common_translations()

        # Use special formatting for node.created
        if event_type == "node.created":
            fields_content = self._format_node_created_fields(data, translations["field_sep"])
        else:
            fields_content = self._format_node_fields(data, translations["field_sep"])

        # Build additional content sections
        additional_content = ""

        # Add last status message if available
        if "lastStatusMessage" in data and data["lastStatusMessage"]:
            status_msg = data["lastStatusMessage"]
            # Only show if not None or empty
            if status_msg and str(status_msg).strip().lower() not in ["none", ""]:
                status_icon = _("field-last-status-icon")
                status_label = _("field-last-status-message")
                additional_content += (
                    f"\n{status_icon} <b>{status_label}:</b> {self.escape_value(status_msg)}"
                )

        # Add connection loss statistics if available
        if event_type == "node.connection_lost" and connection_stats:
            from src.config import config

            stats_icon = _("connection-stats-icon")
            stats_title = _("connection-stats-title", hours=config.CONNECTION_LOSS_STATS_HOURS)
            additional_content += f"\n{stats_icon} <b>{stats_title}:</b>\n{connection_stats}"

        return self.build_standard_message(
            event_type=event_type,
            timestamp=timestamp,
            fields_content=fields_content,
            additional_content=additional_content if additional_content else None,
        )

    def _format_node_created_fields(self, data: Dict[str, Any], field_sep: str) -> str:
        """Format fields specifically for node.created event."""

        def format_address_with_port(value, data):
            """Combine address with port."""
            if "port" in data:
                return f"{value}:{data['port']}"
            return value

        def format_inbound_info(value):
            """Format first inbound information."""
            if not value:
                return None
            inbound = value[0]  # Get first inbound
            protocol = inbound.get("type", "").upper()
            security = inbound.get("security", "")
            port = inbound.get("port", "")

            inbound_info = f"{protocol} protocol"
            if security:
                inbound_info += f" with {security.capitalize()} security"
            if port:
                inbound_info += f" on port {port}"
            return inbound_info

        field_configs = [
            ("name", "field-node-name", True),
            {
                "data_key": "address",
                "translation_key": "field-address",
                "formatter": format_address_with_port,
                "use_code": True,
            },
            ("countryCode", "field-location", False),
            {
                "data_key": "provider",
                "translation_key": "field-provider",
                "use_code": True,
                "nested": "provider.name",
            },
            {
                "data_key": "activeInbounds",
                "translation_key": "field-inbound",
                "formatter": format_inbound_info,
                "condition": lambda d: d.get("activeInbounds"),
            },
        ]

        msg = self._format_fields(data, field_sep, field_configs)
        msg += self._format_inbound_tags(data, field_sep)

        return msg

    def _format_node_fields(self, data: Dict[str, Any], field_sep: str) -> str:
        """Format standard node fields for other node events."""

        def format_traffic(value):
            """Convert bytes to TB."""
            try:
                traffic_bytes = int(value)
                traffic_tb = traffic_bytes / (1024**4)
                return f"{traffic_tb:.2f} TB"
            except (ValueError, TypeError):
                return str(value)

        field_configs = [
            ("name", "field-name", True),
            ("address", "field-address", True),
            ("port", "field-port", True),
            {
                "data_key": "provider",
                "translation_key": "field-provider",
                "use_code": True,
                "nested": "provider.name",
            },
            ("status", "field-status", False),
            ("xrayVersion", "field-xray-version", True),
            ("nodeVersion", "field-node-version", True),
            {
                "data_key": "trafficUsedBytes",
                "translation_key": "field-traffic-used",
                "formatter": format_traffic,
                "use_code": True,
            },
        ]

        msg = self._format_fields(data, field_sep, field_configs)
        msg += self._format_inbound_tags(data, field_sep)

        return msg

    def _format_inbound_tags(self, data: Dict[str, Any], field_sep: str) -> str:
        """Format inbound tags from activeInbounds array."""
        msg = ""

        if "activeInbounds" in data and data["activeInbounds"]:
            # Extract all tags from activeInbounds
            tags = []
            for inbound in data["activeInbounds"]:
                if "tag" in inbound:
                    tags.append(inbound["tag"])

            if tags:
                field_label = _("field-inbound-tags")
                tags_str = ", ".join(tags)
                msg += self.format_field(field_sep, field_label, tags_str, use_code=True)

        return msg
