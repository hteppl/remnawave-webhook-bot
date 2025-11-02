import hashlib
import hmac
import logging
from typing import Dict, Any, List

from aiogram import Bot
from aiohttp import web

from src.config import config
from src.event_filter import event_filter
from src.formatter import MessageFormatter
from src.utils.billing_aggregator import BillingAggregator
from src.utils.connection_tracker import ConnectionLossTracker

logger = logging.getLogger(__name__)


class WebhookHandler:
    def __init__(self, bot: Bot):
        self.bot = bot
        self.formatter = MessageFormatter()
        self.event_filter = event_filter
        self.billing_aggregator = BillingAggregator(
            window_seconds=3, send_callback=self._send_aggregated_billing_notification
        )
        self.connection_tracker = ConnectionLossTracker(
            enabled=config.ENABLE_CONNECTION_LOSS_STATS, window_hours=config.CONNECTION_LOSS_STATS_HOURS
        )

    @staticmethod
    def verify_signature(payload: bytes, signature: str, secret: str) -> bool:
        expected = hmac.new(secret.encode(), payload, hashlib.sha256).hexdigest()
        return hmac.compare_digest(signature, expected)

    async def send_notification(self, message: str, event_type: str):
        try:
            thread_id = config.get_topic_for_event(event_type)
            await self.bot.send_message(
                chat_id=config.TELEGRAM_CHAT_ID, text=message, parse_mode="HTML", message_thread_id=thread_id
            )
            logger.info(f"Notification sent to topic {thread_id}" if thread_id else "Notification sent")
        except Exception as e:
            logger.error(f"Failed to send notification: {e}")

    async def _send_aggregated_billing_notification(self, events: List[Dict[str, Any]]):
        if not events:
            return

        try:
            if len(events) > 1:
                aggregated_msg = self.billing_aggregator.format_aggregated_message(events)
                if aggregated_msg:
                    await self.send_notification(aggregated_msg, events[0]["event_type"])
                    logger.info(f"Sent aggregated billing notification ({len(events)} events)")
                else:
                    for event in events:
                        msg = await self.formatter.format_webhook_message(
                            event["event_type"], event["data"], event["timestamp"], connection_tracker=self.connection_tracker
                        )
                        await self.send_notification(msg, event["event_type"])
            else:
                event = events[0]
                msg = await self.formatter.format_webhook_message(
                    event["event_type"], event["data"], event["timestamp"], connection_tracker=self.connection_tracker
                )
                await self.send_notification(msg, event["event_type"])
        except Exception as e:
            logger.error(f"Error sending billing notification: {e}")

    async def handle_webhook(self, request: web.Request) -> web.Response:
        try:
            signature = request.headers.get("X-Remnawave-Signature")
            if not signature:
                logger.warning("Missing signature")
                return web.Response(status=401, text="Missing signature")

            payload = await request.read()
            if not self.verify_signature(payload, signature, config.WEBHOOK_SECRET_HEADER):
                logger.warning("Invalid signature")
                return web.Response(status=401, text="Invalid signature")

            data = await request.json()
            event_type = data.get("event")
            event_data = data.get("data", {})
            event_timestamp = data.get("timestamp", request.headers.get("X-Remnawave-Timestamp"))

            if not self.event_filter.is_enabled(event_type):
                if config.LOG_DISABLED_EVENTS:
                    logger.debug(f"Event {event_type} disabled")
                    logger.debug(f"Event data: {event_data}")
                return web.Response(status=200, text="OK")

            logger.info(f"Received webhook: {event_type}")
            logger.debug(f"Event data: {event_data}")

            if config.ENABLE_CONNECTION_LOSS_STATS:
                if event_type == "node.connection_lost":
                    self.connection_tracker.record_connection_loss(event_data.get("name", "Unknown"), event_timestamp)

            if "infra_billing" in event_type:
                await self.billing_aggregator.add_event(event_type, event_data, event_timestamp)
                logger.info("Added billing event to aggregator")
            else:
                message = await self.formatter.format_webhook_message(
                    event_type, event_data, event_timestamp, connection_tracker=self.connection_tracker
                )
                await self.send_notification(message, event_type)

            return web.Response(status=200, text="OK")

        except Exception as e:
            logger.error(f"Error processing webhook: {e}")
            return web.Response(status=500, text="Internal server error")

    @staticmethod
    async def health_check(request: web.Request) -> web.Response:
        return web.Response(status=200, text="OK")
