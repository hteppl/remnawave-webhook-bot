import hashlib
import hmac
import logging

from aiogram import Bot
from aiohttp import web

from src.config import config
from src.event_filter import event_filter
from src.formatter import MessageFormatter

logger = logging.getLogger(__name__)


class WebhookHandler:
    """Handle incoming webhook requests."""

    def __init__(self, bot: Bot):
        self.bot = bot
        self.formatter = MessageFormatter()
        self.event_filter = event_filter

    @staticmethod
    def verify_signature(payload: bytes, signature: str, secret: str) -> bool:
        """
        Verify webhook signature using HMAC-SHA256.

        Args:
            payload: Request payload bytes
            signature: Signature from request header
            secret: Secret key for verification

        Returns:
            True if signature is valid, False otherwise
        """
        expected_signature = hmac.new(
            secret.encode(),
            payload,
            hashlib.sha256
        ).hexdigest()
        return hmac.compare_digest(signature, expected_signature)

    async def send_notification(self, message: str, event_type: str):
        """
        Send notification to Telegram.

        Args:
            message: Message text to send
            event_type: Event type for topic routing
        """
        try:
            # Get topic ID for event type
            message_thread_id = config.get_topic_for_event(event_type)

            # Send message
            await self.bot.send_message(
                chat_id=config.TELEGRAM_CHAT_ID,
                text=message,
                parse_mode='HTML',
                message_thread_id=message_thread_id
            )

            if message_thread_id:
                logger.info(f"Notification sent successfully to topic {message_thread_id}")
            else:
                logger.info("Notification sent successfully")
        except Exception as e:
            logger.error(f"Failed to send Telegram notification: {e}")

    async def handle_webhook(self, request: web.Request) -> web.Response:
        """
        Handle incoming webhook requests.

        Args:
            request: Aiohttp web request

        Returns:
            Web response
        """
        try:
            # Get signature from headers
            signature = request.headers.get('X-Remnawave-Signature')
            timestamp = request.headers.get('X-Remnawave-Timestamp')

            if not signature:
                logger.warning("Missing signature header")
                return web.Response(status=401, text="Missing signature")

            # Read payload
            payload = await request.read()

            # Verify signature
            if not self.verify_signature(payload, signature, config.WEBHOOK_SECRET_HEADER):
                logger.warning("Invalid signature")
                return web.Response(status=401, text="Invalid signature")

            # Parse JSON
            data = await request.json()
            event_type = data.get('event')
            event_data = data.get('data', {})
            event_timestamp = data.get('timestamp', timestamp)

            logger.info(f"Received webhook: {event_type}")
            logger.debug(f"Event data: {event_data}")

            # Check if event is enabled
            if not self.event_filter.is_enabled(event_type):
                logger.info(f"Event {event_type} is disabled, skipping notification")
                return web.Response(status=200, text="OK - event disabled")

            # Format and send message
            message = self.formatter.format_webhook_message(
                event_type, event_data, event_timestamp
            )
            await self.send_notification(message, event_type)

            return web.Response(status=200, text="OK")

        except Exception as e:
            logger.error(f"Error processing webhook: {e}")
            return web.Response(status=500, text="Internal server error")

    @staticmethod
    async def health_check(request: web.Request) -> web.Response:
        """
        Health check endpoint without authentication.

        Args:
            request: Aiohttp web request

        Returns:
            Web response with 200 OK
        """
        return web.Response(status=200, text="OK")
