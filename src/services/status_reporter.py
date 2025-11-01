import asyncio
import logging

from aiogram import Bot

from src.config import config
from src.i18n import get_translation as _
from src.utils.connection_tracker import ConnectionLossTracker
from src.utils.timezone_helper import get_current_timestamp

logger = logging.getLogger(__name__)


class StatusReporter:
    def __init__(self, bot: Bot, connection_tracker: ConnectionLossTracker):
        self.bot = bot
        self.connection_tracker = connection_tracker
        self.task = None

    async def start(self):
        if not config.ENABLE_CONNECTION_LOSS_STATS or not config.TOPIC_STATUS:
            logger.info("Status reports disabled")
            return

        logger.info(f"Starting status reporter ({config.CONNECTION_LOSS_REPORT_INTERVAL_HOURS}h interval)")
        self.task = asyncio.create_task(self._periodic_report())

    async def stop(self):
        if self.task:
            self.task.cancel()
            try:
                await self.task
            except asyncio.CancelledError:
                logger.info("Status reporter stopped")

    async def _periodic_report(self):
        interval = config.CONNECTION_LOSS_REPORT_INTERVAL_HOURS * 3600
        while True:
            try:
                await asyncio.sleep(interval)
                await self._send_status_report()
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in status report: {e}", exc_info=True)

    async def _send_status_report(self):
        stats = self.connection_tracker.format_statistics_summary()
        if not stats:
            logger.debug("No statistics to report")
            return

        stats_formatted = "\n".join([f"<code>{line}</code>" for line in stats.split("\n") if line])
        message = (
            f"{_('connection-stats-icon')} <b>{_('connection-stats-title', hours=config.CONNECTION_LOSS_STATS_HOURS)}</b>\n"
            f"{stats_formatted}\n\n"
            f"{_('message-header-time-icon')} <b>{_('message-header-time-label')}:</b> {get_current_timestamp()}"
        )

        try:
            await self.bot.send_message(
                chat_id=config.TELEGRAM_CHAT_ID,
                text=message,
                parse_mode="HTML",
                message_thread_id=int(config.TOPIC_STATUS),
            )
            logger.info("Status report sent")
        except Exception as e:
            logger.error(f"Failed to send status report: {e}", exc_info=True)
