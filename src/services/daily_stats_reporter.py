import asyncio
import logging
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from aiogram import Bot

from src.config import config
from src.i18n import get_translation as _
from src.utils.timezone_helper import get_current_timestamp

logger = logging.getLogger(__name__)


def _parse_report_time() -> tuple[int, int]:
    try:
        parts = config.DAILY_STATS_TIME.split(":")
        hour = int(parts[0])
        minute = int(parts[1]) if len(parts) > 1 else 0
        if not (0 <= hour <= 23 and 0 <= minute <= 59):
            raise ValueError("Invalid time range")
        return hour, minute
    except (ValueError, IndexError) as e:
        logger.warning(f"Invalid DAILY_STATS_TIME '{config.DAILY_STATS_TIME}', using 00:00. Error: {e}")
        return 0, 0


def _get_seconds_until_report_time() -> float:
    try:
        tz = ZoneInfo(config.TIMEZONE)
    except ZoneInfoNotFoundError:
        logger.warning(f"Timezone '{config.TIMEZONE}' not found, using UTC")
        tz = ZoneInfo("UTC")

    hour, minute = _parse_report_time()
    now = datetime.now(tz)
    report_time = now.replace(hour=hour, minute=minute, second=0, microsecond=0)

    if report_time <= now:
        report_time += timedelta(days=1)

    return (report_time - now).total_seconds()


class DailyStatsReporter:
    def __init__(self, bot: Bot):
        self.bot = bot
        self.task = None
        self.users_created = 0
        self.users_first_connected = 0
        self._lock = asyncio.Lock()

    async def record_event(self, event_type: str):
        async with self._lock:
            if event_type == "user.created":
                self.users_created += 1
                logger.debug(f"Recorded user.created event (total: {self.users_created})")
            elif event_type == "user.first_connected":
                self.users_first_connected += 1
                logger.debug(f"Recorded user.first_connected event (total: {self.users_first_connected})")

    async def start(self):
        if not config.ENABLE_DAILY_STATS or not config.TOPIC_STATUS:
            logger.info("Daily stats reports disabled")
            return

        logger.info(f"Starting daily stats reporter (report at {config.DAILY_STATS_TIME})")
        self.task = asyncio.create_task(self._schedule_report())

    async def stop(self):
        if self.task:
            self.task.cancel()
            try:
                await self.task
            except asyncio.CancelledError:
                logger.info("Daily stats reporter stopped")

    async def _schedule_report(self):
        while True:
            try:
                seconds_until_report = _get_seconds_until_report_time()
                logger.info(f"Next daily stats report in {seconds_until_report / 3600:.2f} hours")
                await asyncio.sleep(seconds_until_report)
                await self._send_daily_report()
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in daily stats report: {e}", exc_info=True)
                await asyncio.sleep(60)

    async def _send_daily_report(self):
        async with self._lock:
            users_created = self.users_created
            users_first_connected = self.users_first_connected
            self.users_created = 0
            self.users_first_connected = 0

        if users_created == 0 and users_first_connected == 0:
            logger.debug("No daily stats to report")
            return

        message_parts = [
            f"<b>{_('daily-stats-title')}</b>",
            "",
            f"<b>{_('daily-stats-users-created')}:</b> {users_created}",
            f"<b>{_('daily-stats-users-first-connected')}:</b> {users_first_connected}",
            "",
            f"<b>{_('message-header-time')}:</b> {get_current_timestamp()}",
        ]
        message = "\n".join(message_parts)

        try:
            await self.bot.send_message(
                chat_id=config.TELEGRAM_CHAT_ID,
                text=message,
                parse_mode="HTML",
                message_thread_id=int(config.TOPIC_STATUS),
            )
            logger.info(f"Daily stats report sent (created: {users_created}, first_connected: {users_first_connected})")
        except Exception as e:
            logger.error(f"Failed to send daily stats report: {e}", exc_info=True)
