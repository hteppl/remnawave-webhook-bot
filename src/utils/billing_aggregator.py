import asyncio
import logging
from collections import defaultdict
from datetime import datetime
from typing import Dict, List, Any, Optional

from src.i18n import get_translation as _
from src.utils.timezone_helper import format_timestamp

logger = logging.getLogger(__name__)


class BillingAggregator:
    """Aggregates multiple billing notifications received within a time window."""

    def __init__(self, window_seconds: int = 3, send_callback=None):
        """
        Initialize the billing aggregator.

        Args:
            window_seconds: Time window in seconds to wait for aggregating notifications
            send_callback: Async callback function to send notifications
        """
        self.window_seconds = window_seconds
        self.pending_events = []
        self.processing_task = None
        self.send_callback = send_callback

    async def add_event(self, event_type: str, data: Dict[str, Any], timestamp: str) -> str:
        """
        Add a billing event for potential aggregation.

        Returns:
            Event ID for tracking
        """
        event_id = f"billing_{timestamp}_{data.get('nodeName', 'unknown')}"

        self.pending_events.append({"event_type": event_type, "data": data, "timestamp": timestamp})

        # Start aggregation timer if not already running
        if not self.processing_task:
            self.processing_task = asyncio.create_task(self._process_batch())
            logger.info(f"Started aggregation timer for {self.window_seconds} seconds")

        return event_id

    async def _process_batch(self):
        """Process a batch of events after the time window expires."""
        await asyncio.sleep(self.window_seconds)

        logger.info(f"Processing batch of {len(self.pending_events)} billing events")
        events = self.pending_events.copy()
        self.pending_events.clear()
        self.processing_task = None

        if events and self.send_callback:
            await self.send_callback(events)

        return events

    def format_aggregated_message(self, events: List[Dict[str, Any]]) -> Optional[str]:
        """Format an aggregated message for multiple billing events."""
        if not events or len(events) == 0:
            return None  # No events to format

        if len(events) == 1:
            return None  # Let the normal formatter handle single events

        # Get field labels
        header_icon = _("event-crm-header-icon")
        billing_notifications_title = _("billing-aggregated-title")
        total_nodes_label = _("billing-field-total-nodes")
        nodes_label = _("billing-field-nodes")
        time_icon = _("message-header-time-icon")
        time_label = _("message-header-time-label")

        # Build message
        msg = f"{header_icon} <b>{billing_notifications_title}</b>\n"
        msg += f"<b>{total_nodes_label}:</b> {len(events)}\n\n"

        # Group by provider
        by_provider = defaultdict(list)
        for event in events:
            provider = event["data"].get("providerName", "Unknown")
            by_provider[provider].append(event)

        for provider, provider_events in by_provider.items():
            msg += f"<b>{provider}</b> ({len(provider_events)} {nodes_label}):\n"

            for event in provider_events:
                node_name = event["data"].get("nodeName", "Unknown")
                billing_date = event["data"].get("nextBillingAt", "")
                event_name = self.get_event_name(event["event_type"])
                event_icon = _(f"event-crm-{event_name}-icon")

                # Format date
                if billing_date:
                    try:
                        dt = datetime.fromisoformat(billing_date.replace("Z", "+00:00"))
                        formatted_date = dt.strftime("%b %d, %H:%M UTC")
                    except (Exception,):
                        formatted_date = billing_date[:10] if len(billing_date) > 10 else billing_date
                else:
                    formatted_date = "N/A"

                msg += f"  {event_icon} <code>{node_name}</code> - {formatted_date}\n"

            # Add provider login link if available
            login_url = provider_events[0]["data"].get("loginUrl")
            if login_url:
                login_text = _("billing-field-login-to-provider", provider=provider)
                msg += f'  🔗 <a href="{login_url}">{login_text}</a>\n'
            msg += "\n"

        # Add timestamp
        if events:
            formatted_timestamp = format_timestamp(events[0]["timestamp"])
            msg += f"{time_icon} <b>{time_label}:</b> {formatted_timestamp}"

        return msg

    def get_event_name(self, event_type: str) -> str:
        """Extract event name from event type."""
        # Convert event type like "crm.infra_billing_node_payment_in_48hrs"
        # to "infra-billing-node-payment-in-48hrs"
        return event_type.replace(".", "-").replace("_", "-")

    async def get_pending_count(self) -> int:
        """Get count of pending events."""
        return len(self.pending_events)
