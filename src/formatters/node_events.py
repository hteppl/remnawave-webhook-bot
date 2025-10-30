from typing import Dict, Any

from src.formatters.base import BaseEventFormatter
from src.i18n import get_translation as _


class NodeEventFormatter(BaseEventFormatter):
    """Formatter for node-related events."""

    async def format(self, event_type: str, data: Dict[str, Any], timestamp: str, connection_stats: str = None,
                     **kwargs) -> str:
        """Format node event data."""
        translations = self.get_common_translations()

        # Use special formatting for node.created
        if event_type == "node.created":
            fields_content = self._format_node_created_fields(data, translations["field_sep"])
        else:
            fields_content = self._format_node_fields(data, translations["field_sep"])

        # Add connection loss statistics if available
        additional_content = None
        if event_type == "node.connection_lost" and connection_stats:
            from src.config import config

            stats_icon = _("connection-stats-icon")
            stats_title = _("connection-stats-title", hours=config.CONNECTION_LOSS_STATS_HOURS)
            additional_content = f"\n{stats_icon} <b>{stats_title}</b>\n<pre>{connection_stats}</pre>"

        return self.build_standard_message(
            event_type=event_type,
            timestamp=timestamp,
            fields_content=fields_content,
            additional_content=additional_content,
        )

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

        # Inbound tags
        msg += self._format_inbound_tags(data, field_sep)

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

        # Port
        if "port" in data:
            field_label = _("field-port")
            msg += self.format_field(field_sep, field_label, data["port"])

        # Provider
        if "provider" in data and isinstance(data["provider"], dict) and "name" in data["provider"]:
            field_label = _("field-provider")
            msg += self.format_field(field_sep, field_label, data["provider"]["name"], use_code=True)

        # Status
        if "status" in data:
            field_label = _("field-status")
            msg += self.format_field(field_sep, field_label, data["status"])

        # Last Status Message
        if "lastStatusMessage" in data:
            field_label = _("field-last-status-message")
            msg += self.format_field(field_sep, field_label, data["lastStatusMessage"])

        # Xray Version
        if "xrayVersion" in data:
            field_label = _("field-xray-version")
            msg += self.format_field(field_sep, field_label, data["xrayVersion"], use_code=True)

        # Node Version
        if "nodeVersion" in data:
            field_label = _("field-node-version")
            msg += self.format_field(field_sep, field_label, data["nodeVersion"], use_code=True)

        # Traffic Used (convert to TB)
        if "trafficUsedBytes" in data:
            field_label = _("field-traffic-used")
            try:
                traffic_bytes = int(data["trafficUsedBytes"])
                traffic_tb = traffic_bytes / (1024**4)  # Convert bytes to TB
                traffic_str = f"{traffic_tb:.2f} TB"
            except (ValueError, TypeError):
                traffic_str = str(data["trafficUsedBytes"])
            msg += self.format_field(field_sep, field_label, traffic_str)

        # CPU Model
        if "cpuModel" in data:
            field_label = _("field-cpu-model")
            msg += self.format_field(field_sep, field_label, data["cpuModel"])

        # CPU Count
        if "cpuCount" in data:
            field_label = _("field-cpu-count")
            msg += self.format_field(field_sep, field_label, data["cpuCount"])

        # Total RAM
        if "totalRam" in data:
            field_label = _("field-total-ram")
            msg += self.format_field(field_sep, field_label, data["totalRam"])

        # Inbound tags
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
