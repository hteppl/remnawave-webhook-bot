from typing import Dict, Any

from src.formatters.base import BaseEventFormatter
from src.i18n import get_translation as _
from src.utils.timezone_helper import format_timestamp


class TorrentBlockerEventFormatter(BaseEventFormatter):
    """Formatter for `torrent_blocker.*` events (Remnawave v2.7.0+).

    Payload: `{"node": {...}, "user": {...}, "report": {"actionReport": {...}, "xrayReport": {...}}}`.
    """

    async def format(self, event_type: str, data: Dict[str, Any], timestamp: str, **kwargs) -> str:
        t = self.get_common_translations()
        field_sep = t["field_sep"]

        node = self._section(data, "node")
        user = self._section(data, "user")
        report = self._section(data, "report")
        # Older builds may send the reports at the top level instead of under `report`.
        action = self._section(report, "actionReport") or self._section(data, "actionReport")
        xray = self._section(report, "xrayReport") or self._section(data, "xrayReport")

        msg = ""
        if username := user.get("username"):
            msg += self.format_field(field_sep, _("field-username"), username, use_code=True)
        if node_name := node.get("name"):
            msg += self.format_field(field_sep, _("field-node-name"), node_name, use_code=True)
        if country := node.get("countryCode"):
            msg += self.format_field(field_sep, _("field-location"), country)

        blocked = action.get("blocked", action.get("isBlocked"))
        if blocked is not None:
            msg += self.format_field(field_sep, _("field-blocked"), _("value-yes") if blocked else _("value-no"))
        if ip := action.get("ip"):
            msg += self.format_field(field_sep, _("field-ip"), ip, use_code=True)
        if duration := action.get("blockDuration"):
            msg += self.format_field(field_sep, _("field-block-duration"), self._format_duration(duration))
        if unblock_at := action.get("willUnblockAt"):
            msg += self.format_field(field_sep, _("field-unblock-at"), format_timestamp(unblock_at))

        for key, translation_key in (
            ("protocol", "field-protocol"),
            ("network", "field-network"),
            ("source", "field-source"),
            ("destination", "field-destination"),
        ):
            if value := xray.get(key):
                msg += self.format_field(field_sep, _(translation_key), value, use_code=True)

        for key, translation_key in (("inboundTag", "field-inbound-tag"), ("outboundTag", "field-outbound-tag")):
            if value := xray.get(key):
                msg += self.format_field(field_sep, _(translation_key), value, use_code=True)

        return self.build_standard_message(
            event_type=event_type,
            timestamp=timestamp,
            fields_content=msg,
        )

    @staticmethod
    def _format_duration(seconds: Any) -> str:
        """Render `blockDuration` (seconds) as a compact human-readable span."""
        try:
            total = int(seconds)
        except (TypeError, ValueError):
            return str(seconds)
        if total < 60:
            return _("duration-seconds", seconds=total)
        if total < 3600:
            return _("duration-minutes", minutes=total // 60)
        if total < 86400:
            return _("duration-hours", hours=total // 3600)
        return _("duration-days", days=total // 86400)

    @staticmethod
    def _section(data: Dict[str, Any], key: str) -> Dict[str, Any]:
        value = data.get(key)
        return value if isinstance(value, dict) else {}
