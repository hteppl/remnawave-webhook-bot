import logging
from typing import Any

from src.formatters.base import BaseEventFormatter
from src.l10n import get_translation as _
from src.services import IPGeolocationService
from src.utils.timezone_helper import format_timestamp
from src.utils.user_agent_parser import get_device_info

logger = logging.getLogger(__name__)


class ServiceEventFormatter(BaseEventFormatter):
    """Formatter for service-related events."""

    def __init__(self):
        self.geo_service = IPGeolocationService()

    async def format(self, event_type: str, data: dict[str, Any], timestamp: str, **kwargs) -> str:
        """Format service event data."""
        translations = self.get_common_translations()
        icon = self.get_event_icon(event_type)
        event_message = self.get_event_message(event_type)

        if icon:
            msg = f"{icon} <b>{translations['action']}:</b> {event_message}\n\n"
        else:
            msg = f"<b>{translations['action']}:</b> {event_message}\n\n"

        if event_type in ("service.login_attempt_failed", "service.login_attempt_success"):
            msg += await self._format_service_fields(data, translations["field_sep"])
            msg += "\n"
        elif fields := self._format_simple_fields(event_type, data, translations["field_sep"]):
            msg += fields + "\n"

        msg += f"<b>{translations['time']}:</b> {format_timestamp(timestamp)}"

        return msg

    def _format_simple_fields(self, event_type: str, data: dict[str, Any], field_sep: str) -> str:
        """Fields for non-login service events (subpage config, API tokens)."""
        if event_type == "service.subpage_config_changed":
            subpage = data.get("subpageConfig")
            if not isinstance(subpage, dict):
                return ""
            return self._format_fields(
                subpage,
                field_sep,
                [
                    ("action", "field-action", False),
                    ("uuid", "field-uuid", True),
                ],
            )

        if event_type.startswith("service.api_token_"):
            token = data.get("apiToken")
            if not isinstance(token, dict):
                return ""
            msg = self._format_fields(
                token,
                field_sep,
                [
                    ("name", "field-name", True),
                    ("uuid", "field-uuid", True),
                ],
            )
            if scopes := token.get("scopes"):
                msg += self.format_field(field_sep, _("field-scopes"), ", ".join(scopes), use_code=True)
            if expire_at := token.get("expireAt"):
                msg += self.format_field(field_sep, _("field-expire"), format_timestamp(expire_at))
            return msg

        return ""

    async def _format_service_fields(self, data: dict[str, Any], field_sep: str) -> str:
        """Format service-specific fields with geolocation."""
        flattened_data = {}
        for key, value in data.items():
            if isinstance(value, dict):
                flattened_data.update(value)
            else:
                flattened_data[key] = value

        field_configs = [
            ("ip", "field-ip", True),
        ]

        msg = self._format_fields(flattened_data, field_sep, field_configs)

        ip_address = flattened_data.get("ip")
        if ip_address:
            geo_data = await self.geo_service.get_location(ip_address)

            if geo_data:
                if geo_data.get("country"):
                    field_label = _("field-geo-country")
                    value = (
                        f"{geo_data['country']} ({geo_data['countryCode']})"
                        if geo_data.get("countryCode")
                        else geo_data["country"]
                    )
                    msg += self.format_field(field_sep, field_label, value)

                if geo_data.get("city") or geo_data.get("regionName"):
                    field_label = _("field-geo-city")
                    parts = []
                    if geo_data.get("city"):
                        parts.append(geo_data["city"])
                    if geo_data.get("regionName"):
                        parts.append(geo_data["regionName"])
                    value = ", ".join(parts)
                    msg += self.format_field(field_sep, field_label, value)

                if geo_data.get("isp"):
                    field_label = _("field-geo-isp")
                    msg += self.format_field(field_sep, field_label, geo_data["isp"])

        user_agent = flattened_data.get("userAgent")
        if user_agent:
            device_info = get_device_info(user_agent)
            if device_info:
                field_label = _("field-device")
                msg += self.format_field(field_sep, field_label, device_info)

        remaining_configs = [
            ("userAgent", "field-user-agent", False),
            ("username", "field-username", True),
            ("password", "field-password", True),
        ]

        msg += self._format_fields(flattened_data, field_sep, remaining_configs)

        return msg
