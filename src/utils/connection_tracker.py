import logging
from datetime import datetime, timezone
from typing import Dict, List, Optional

from src.utils.timestamped_storage import TimestampedStorage

logger = logging.getLogger(__name__)


class ConnectionLossTracker:
    def __init__(self, enabled: bool = False, window_hours: int = 24):
        self.enabled = enabled
        self.window_hours = window_hours
        self.storage = TimestampedStorage()
        self.down_times: Dict[str, datetime] = {}
        logger.info(
            f"Connection loss tracker: {'enabled' if enabled else 'disabled'}"
            + (f" (window={window_hours}h)" if enabled else "")
        )

    def record_connection_loss(self, node_name: str, timestamp: str = None) -> None:
        if not self.enabled:
            return

        dt = None
        if timestamp:
            try:
                dt = datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
            except Exception as e:
                logger.warning(f"Failed to parse timestamp '{timestamp}': {e}")

        if dt is None:
            dt = datetime.now(timezone.utc)

        self.storage.add(key=node_name, value=1, timestamp=dt)
        self.down_times[node_name] = dt
        logger.info(f"Recorded connection loss for node: {node_name}")

    def get_statistics(self) -> Dict[str, int]:
        if not self.enabled:
            return {}

        stats = {}
        for node_name in self.storage.get_all_keys():
            if count := self.storage.count_recent(node_name, self.window_hours):
                stats[node_name] = count

        logger.debug(f"Retrieved statistics for {len(stats)} nodes")
        return stats

    def get_node_loss_count(self, node_name: str) -> int:
        return self.storage.count_recent(node_name, self.window_hours) if self.enabled else 0

    def get_statistics_lines(self) -> List[str]:
        if not self.enabled:
            return []

        stats = self.get_statistics()
        if not stats:
            return []

        sorted_stats = sorted(stats.items(), key=lambda x: (-x[1], x[0]))
        return [f"<code>{name}</code> - x{count}" for name, count in sorted_stats]

    def get_storage_stats(self) -> Dict[str, int]:
        return self.storage.get_stats()

    def get_downtime(self, node_name: str, restore_timestamp: str = None) -> Optional[str]:
        if not self.enabled or node_name not in self.down_times:
            return None

        down_time = self.down_times[node_name]

        restore_time = None
        if restore_timestamp:
            try:
                restore_time = datetime.fromisoformat(restore_timestamp.replace("Z", "+00:00"))
            except Exception as e:
                logger.warning(f"Failed to parse restore timestamp '{restore_timestamp}': {e}")

        if restore_time is None:
            restore_time = datetime.now(timezone.utc)

        duration = restore_time - down_time
        total_seconds = int(duration.total_seconds())

        del self.down_times[node_name]

        if total_seconds < 60:
            return f"{total_seconds}s"
        elif total_seconds < 3600:
            minutes = total_seconds // 60
            seconds = total_seconds % 60
            return f"{minutes}m {seconds}s"
        elif total_seconds < 86400:
            hours = total_seconds // 3600
            minutes = (total_seconds % 3600) // 60
            return f"{hours}h {minutes}m"
        else:
            days = total_seconds // 86400
            hours = (total_seconds % 86400) // 3600
            return f"{days}d {hours}h"
