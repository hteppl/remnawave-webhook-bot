import asyncio
import logging
from collections import defaultdict
from datetime import datetime
from typing import Dict, List, Any, Optional

from src.i18n import get_translation as _
from src.utils.timezone_helper import format_timestamp

logger = logging.getLogger(__name__)


class BillingAggregator:
    def __init__(self, window_seconds: int = 3, send_callback=None):
        self.window_seconds = window_seconds
        self.pending_events = []
        self.processing_task = None
        self.send_callback = send_callback

    async def add_event(self, event_type: str, data: Dict[str, Any], timestamp: str) -> str:
        event_id = f"billing_{timestamp}_{data.get('nodeName', 'unknown')}"
        self.pending_events.append({"event_type": event_type, "data": data, "timestamp": timestamp})

        if not self.processing_task:
            self.processing_task = asyncio.create_task(self._process_batch())
            logger.info(f"Started aggregation timer ({self.window_seconds}s)")

        return event_id

    async def _process_batch(self):
        await asyncio.sleep(self.window_seconds)
        logger.info(f"Processing {len(self.pending_events)} billing events")

        events = self.pending_events.copy()
        self.pending_events.clear()
        self.processing_task = None

        if events and self.send_callback:
            await self.send_callback(events)

        return events

    def format_aggregated_message(self, events: List[Dict[str, Any]]) -> Optional[str]:
        if not events or len(events) <= 1:
            return None

        msg = f"<b>{_('billing-aggregated-title')}</b>\n"
        msg += f"<b>{_('billing-field-total-nodes')}:</b> {len(events)}\n\n"

        by_provider = defaultdict(list)
        for event in events:
            by_provider[event["data"].get("providerName", "Unknown")].append(event)

        for provider, provider_events in by_provider.items():
            msg += f"<b>{provider}</b> ({len(provider_events)} {_('billing-field-nodes')}):\n"

            for event in provider_events:
                node_name = event["data"].get("nodeName", "Unknown")
                billing_date = event["data"].get("nextBillingAt", "")

                if billing_date:
                    try:
                        dt = datetime.fromisoformat(billing_date.replace("Z", "+00:00"))
                        formatted_date = dt.strftime("%b %d, %H:%M UTC")
                    except Exception:
                        formatted_date = billing_date[:10] if len(billing_date) > 10 else billing_date
                else:
                    formatted_date = "N/A"

                msg += f"  • <code>{node_name}</code> - {formatted_date}\n"

            if login_url := provider_events[0]["data"].get("loginUrl"):
                msg += f'  🔗 <a href="{login_url}">{_("billing-field-login-to-provider", provider=provider)}</a>\n'
            msg += "\n"

        msg += f"<b>{_('message-header-time')}:</b> {format_timestamp(events[0]['timestamp'])}"
        return msg

    async def get_pending_count(self) -> int:
        return len(self.pending_events)
