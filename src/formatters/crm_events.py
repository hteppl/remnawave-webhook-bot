from datetime import datetime
from typing import Dict, Any

from src.formatters.base import BaseEventFormatter
from src.i18n import get_translation as _


class CRMEventFormatter(BaseEventFormatter):
    """Formatter for CRM-related events."""

    async def format(self, event_type: str, data: Dict[str, Any], timestamp: str, **kwargs) -> str:
        """Format CRM event data."""
        # Check if this is a billing event
        if "infra_billing" in event_type:
            return await self._format_billing_event(event_type, data, timestamp)

        translations = self.get_common_translations()
        fields_content = self._format_crm_fields(data, translations["field_sep"])

        return self.build_standard_message(
            event_type=event_type,
            timestamp=timestamp,
            fields_content=fields_content,
        )

    async def _format_billing_event(self, event_type: str, data: Dict[str, Any], timestamp: str) -> str:
        """Format billing notification events."""
        event_name = self.get_event_name(event_type)

        # Get event-specific translations
        event_icon = _(f"event-crm-{event_name}-icon")
        event_message = _(f"event-crm-{event_name}-message")

        # Get general billing translations
        node_label = _("billing-field-node")
        provider_label = _("billing-field-provider")
        billing_date_label = _("billing-field-billing-date")
        time_icon = _("message-header-time-icon")
        time_label = _("message-header-time-label")

        # Format billing date
        billing_date = data.get("nextBillingAt", "")
        formatted_date = ""
        if billing_date:
            try:
                dt = datetime.fromisoformat(billing_date.replace("Z", "+00:00"))
                formatted_date = dt.strftime("%B %d, %Y at %H:%M UTC")
            except (Exception,):
                formatted_date = billing_date

        # Build message
        msg = f"{event_icon} <b>{event_message}</b>\n\n"
        msg += f"<b>{node_label}:</b> <code>{data.get('nodeName', 'Unknown')}</code>\n"
        msg += f"<b>{provider_label}:</b> {data.get('providerName', 'Unknown')}\n"
        msg += f"<b>{billing_date_label}:</b> {formatted_date}\n"

        if data.get("loginUrl"):
            provider_name = data.get("providerName", "Provider")
            login_text = _("billing-field-login-to-provider", provider=provider_name)
            msg += f'\n<a href="{data["loginUrl"]}">{login_text}</a>\n'

        msg += f"\n{time_icon} <b>{time_label}:</b> {timestamp}"

        return msg

    def _format_crm_fields(self, data: Dict[str, Any], field_sep: str) -> str:
        """Format CRM-specific fields."""
        field_configs = [
            ('username', 'field-username', True),
            ('email', 'field-email', False),
            ('description', 'field-description', False),
            ('status', 'field-status', False),
        ]

        return self._format_fields(data, field_sep, field_configs)
