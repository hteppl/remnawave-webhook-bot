"""Periodic status report service."""

import asyncio
import logging
from datetime import datetime, timezone

from aiogram import Bot

from src.config import config
from src.i18n import get_translation as _
from src.utils.connection_tracker import ConnectionLossTracker

logger = logging.getLogger(__name__)


class StatusReporter:
    """Sends periodic status reports to the status topic."""

    def __init__(self, bot: Bot, connection_tracker: ConnectionLossTracker):
        """
        Initialize the status reporter.

        Args:
            bot: Telegram bot instance
            connection_tracker: Connection loss tracker instance
        """
        self.bot = bot
        self.connection_tracker = connection_tracker
        self.task = None

    async def start(self):
        """Start the periodic status report task."""
        if not config.ENABLE_CONNECTION_LOSS_STATS or not config.TOPIC_STATUS:
            logger.info("Status reports disabled (ENABLE_CONNECTION_LOSS_STATS=false or TOPIC_STATUS not set)")
            return

        interval_hours = config.CONNECTION_LOSS_REPORT_INTERVAL_HOURS
        logger.info(f"Starting status reporter with {interval_hours}h interval")
        self.task = asyncio.create_task(self._periodic_report())

    async def stop(self):
        """Stop the periodic status report task."""
        if self.task:
            self.task.cancel()
            try:
                await self.task
            except asyncio.CancelledError:
                logger.info("Status reporter stopped")

    async def _periodic_report(self):
        """Send periodic status reports."""
        interval_seconds = config.CONNECTION_LOSS_REPORT_INTERVAL_HOURS * 3600

        while True:
            try:
                await asyncio.sleep(interval_seconds)
                await self._send_status_report()
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in periodic status report: {e}", exc_info=True)

    async def _send_status_report(self):
        """Format and send a status report."""
        # Get connection statistics
        stats_summary = self.connection_tracker.format_statistics_summary()

        if not stats_summary:
            logger.debug("No connection loss statistics to report")
            return

        # Format message
        stats_icon = _("connection-stats-icon")
        stats_title = _("connection-stats-title", hours=config.CONNECTION_LOSS_STATS_HOURS)
        time_icon = _("message-header-time-icon")
        time_label = _("message-header-time-label")
        timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")

        # Wrap each stat line in code tags
        stats_lines = stats_summary.split('\n')
        stats_formatted = '\n'.join([f"<code>{line}</code>" for line in stats_lines if line])

        message = (
            f"{stats_icon} <b>{stats_title}</b>\n"
            f"{stats_formatted}\n\n"
            f"{time_icon} <b>{time_label}:</b> {timestamp}"
        )

        # Send to status topic
        try:
            await self.bot.send_message(
                chat_id=config.TELEGRAM_CHAT_ID,
                text=message,
                parse_mode="HTML",
                message_thread_id=int(config.TOPIC_STATUS),
            )
            logger.info(f"Status report sent to TOPIC_STATUS")
        except Exception as e:
            logger.error(f"Failed to send status report: {e}", exc_info=True)
