from typing import Dict, Any

from src.formatters.base import BaseEventFormatter
from src.i18n import get_translation as _


class NodeEventFormatter(BaseEventFormatter):
    async def format(self, event_type: str, data: Dict[str, Any], timestamp: str, **kwargs) -> str:
        t = self.get_common_translations()
        fields_content = (
            self._format_node_created_fields(data, t["field_sep"])
            if event_type == "node.created"
            else self._format_node_fields(data, t["field_sep"])
        )

        additional_content = ""
        if "lastStatusMessage" in data and data["lastStatusMessage"]:
            status_msg = data["lastStatusMessage"]
            if status_msg and str(status_msg).strip().lower() not in ["none", ""]:
                additional_content = f"{_('field-last-status-icon')} <b>{_('field-last-status-message')}:</b> {self.escape_value(status_msg)}"

        return self.build_standard_message(
            event_type=event_type,
            timestamp=timestamp,
            fields_content=fields_content,
            additional_content=additional_content if additional_content else None,
        )

    def _format_node_created_fields(self, data: Dict[str, Any], field_sep: str) -> str:
        def format_address_with_port(value, data):
            return f"{value}:{data['port']}" if "port" in data else value

        def format_inbound_info(value):
            if not value:
                return None
            inbound = value[0]
            info = f"{inbound.get('type', '').upper()} protocol"
            if security := inbound.get("security"):
                info += f" with {security.capitalize()} security"
            if port := inbound.get("port"):
                info += f" on port {port}"
            return info

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
        def format_traffic(value):
            try:
                return f"{int(value) / (1024**4):.2f} TB"
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
        if "activeInbounds" in data and data["activeInbounds"]:
            tags = [inbound["tag"] for inbound in data["activeInbounds"] if "tag" in inbound]
            if tags:
                return self.format_field(field_sep, _("field-inbound-tags"), ", ".join(tags), use_code=True)
        return ""
