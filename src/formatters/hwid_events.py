from typing import Dict, Any

from src.formatters.base import BaseEventFormatter
from src.i18n import get_translation as _
from src.utils.user_agent_parser import get_device_info


class UserHwidDevicesEventFormatter(BaseEventFormatter):
    """Formatter for `user_hwid_devices.*` events.

    Payload: `{"user": {...}, "hwidUserDevice": {...}}`.
    """

    async def format(self, event_type: str, data: Dict[str, Any], timestamp: str, **kwargs) -> str:
        t = self.get_common_translations()
        field_sep = t["field_sep"]
        flat = self.flatten(data, "user", "hwidUserDevice")

        field_configs = [
            ("username", "field-username", True),
            ("hwid", "field-hwid", True),
            ("platform", "field-platform", False),
            ("osVersion", "field-os-version", False),
            ("deviceModel", "field-device-model", False),
        ]

        msg = self._format_fields(flat, field_sep, field_configs)

        if (limit := flat.get("hwidDeviceLimit")) is not None:
            msg += self.format_field(field_sep, _("field-hwid-limit"), limit)

        if user_agent := flat.get("userAgent"):
            if device_info := get_device_info(user_agent):
                msg += self.format_field(field_sep, _("field-device"), device_info)
            msg += self.format_field(field_sep, _("field-user-agent"), user_agent)

        if request_ip := flat.get("requestIp"):
            msg += self.format_field(field_sep, _("field-ip"), request_ip, use_code=True)

        return self.build_standard_message(
            event_type=event_type,
            timestamp=timestamp,
            fields_content=msg,
        )
