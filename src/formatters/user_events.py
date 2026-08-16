from typing import Dict, Any

from src.formatters.base import BaseEventFormatter
from src.i18n import get_translation as _
from src.utils import format_date_with_days


class UserEventFormatter(BaseEventFormatter):
    """Formatter for user-related events."""

    async def format(self, event_type: str, data: Dict[str, Any], timestamp: str, **kwargs) -> str:
        """Format user event data."""
        translations = self.get_common_translations()
        data = self.flatten(data, "userTraffic")
        fields_content = self._format_user_fields(data, translations["field_sep"])

        # Pass usage_percentage for bandwidth events
        event_message_kwargs = {"usage_percentage": self._usage_percentage(data)}

        # `meta` arrives as a top-level sibling of `data`; older payloads may nest it.
        meta = kwargs.get("meta") or data.get("meta")
        message_override, icon_override = self._resolve_meta_message(event_type, meta)

        return self.build_standard_message(
            event_type=event_type,
            timestamp=timestamp,
            fields_content=fields_content,
            event_message_kwargs=event_message_kwargs,
            event_message_override=message_override,
            icon_override=icon_override,
        )

    @staticmethod
    def _usage_percentage(data: Dict[str, Any]) -> int:
        """Threshold percentage for `user.bandwidth_usage_threshold_reached`.

        The panel reports it as `lastTriggeredThreshold`; fall back to computing it from
        traffic counters when that field is absent.
        """
        threshold = data.get("lastTriggeredThreshold", data.get("usage_percentage"))
        if threshold is not None:
            try:
                return int(threshold)
            except (TypeError, ValueError):
                pass

        try:
            limit = int(data.get("trafficLimitBytes") or 0)
            used = int(data.get("usedTrafficBytes") or 0)
        except (TypeError, ValueError):
            return 0
        return int(used / limit * 100) if limit > 0 else 0

    @staticmethod
    def _resolve_meta_message(event_type: str, meta: Any) -> tuple[str | None, str | None]:
        """Build message/icon for notification-style events carrying a `meta` object.

        `user.expiration` replaces the removed `user.expires_in_*` / `user.expired_24_hours_ago`
        events: `meta.expiration` is a signed hour offset — negative means "expires in N hours",
        positive means "expired N hours ago".
        """
        if not isinstance(meta, dict):
            return None, None

        if event_type == "user.expiration":
            expiration = meta.get("expiration")
            if expiration is None:
                return None, None
            try:
                offset = int(expiration)
            except (TypeError, ValueError):
                return None, None
            hours = abs(offset)
            if offset < 0:
                icon = "⏰" if hours > 24 else "⚠️"
                return _("event-user-expiration-in-message", hours=hours), icon
            return _("event-user-expiration-ago-message", hours=hours), "❌"

        if event_type == "user.not_connected":
            hours = meta.get("notConnectedAfterHours")
            if hours is None:
                return None, None
            try:
                hours = int(hours)
            except (TypeError, ValueError):
                return None, None
            return _("event-user-not-connected-hours-message", hours=hours), None

        return None, None

    def _format_user_fields(self, data: Dict[str, Any], field_sep: str) -> str:
        """Format user-specific fields."""

        def format_used_traffic(value):
            """Convert bytes to human-readable format (MB/GB)."""
            used_bytes = int(value)
            if used_bytes == 0:
                return "0 GB"
            elif used_bytes < 1024**3:  # Less than 1 GB
                used_mb = used_bytes / (1024**2)
                return f"{used_mb:.2f} MB"
            else:
                used_gb = used_bytes / (1024**3)
                return f"{used_gb:.2f} GB"

        def format_traffic_limit(value):
            """Convert bytes to human-readable format (GB or Unlimited)."""
            limit_bytes = int(value)
            if limit_bytes == 0:
                return _("date-unlimited")
            else:
                limit_gb = limit_bytes / (1024**3)
                return f"{limit_gb:.2f} GB"

        def format_date(value):
            """Format date with days."""
            return format_date_with_days(value, _)

        def format_squads(value):
            """Format squads list."""
            return ", ".join([squad["name"] for squad in value])

        field_configs = [
            ("username", "field-username", True),
            ("email", "field-email", False),
            ("status", "field-status", False),
            {
                "data_key": "usedTrafficBytes",
                "translation_key": "field-used-traffic",
                "formatter": format_used_traffic,
            },
            {
                "data_key": "trafficLimitBytes",
                "translation_key": "field-data-limit",
                "formatter": format_traffic_limit,
            },
            {
                "data_key": "expireAt",
                "translation_key": "field-expire",
                "formatter": format_date,
                "condition": lambda d: d.get("expireAt"),
            },
            {
                "data_key": "createdAt",
                "translation_key": "field-created-at",
                "formatter": format_date,
                "condition": lambda d: d.get("createdAt"),
            },
            {
                "data_key": "activeInternalSquads",
                "translation_key": "field-squads",
                "use_code": True,
                "formatter": format_squads,
                "condition": lambda d: d.get("activeInternalSquads"),
            },
        ]

        return self._format_fields(data, field_sep, field_configs)
