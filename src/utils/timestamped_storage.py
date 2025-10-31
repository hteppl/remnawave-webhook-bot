import logging
from collections import defaultdict
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List, Tuple

logger = logging.getLogger(__name__)


class TimestampedStorage:
    """Abstract in-memory key-value storage with timestamps."""

    def __init__(self):
        """Initialize the storage."""
        # Structure: {key: [(timestamp, value), ...]}
        self._storage: Dict[str, List[Tuple[datetime, Any]]] = defaultdict(list)

    def add(self, key: str, value: Any, timestamp: datetime = None) -> None:
        """
        Add a value to the storage with a timestamp.

        Args:
            key: Storage key
            value: Value to store
            timestamp: Optional timestamp (defaults to now)
        """
        if timestamp is None:
            timestamp = datetime.now(timezone.utc)

        self._storage[key].append((timestamp, value))
        logger.debug(f"Added to storage: key={key}, value={value}, timestamp={timestamp}")

    def get_all(self, key: str) -> List[Tuple[datetime, Any]]:
        """
        Get all values for a key.

        Args:
            key: Storage key

        Returns:
            List of (timestamp, value) tuples
        """
        return self._storage.get(key, [])

    def get_recent(self, key: str, hours: int) -> List[Tuple[datetime, Any]]:
        """
        Get values for a key within the last N hours.
        Automatically cleans up old data for this key.

        Args:
            key: Storage key
            hours: Number of hours to look back

        Returns:
            List of (timestamp, value) tuples within the time window
        """
        cutoff_time = datetime.now(timezone.utc) - timedelta(hours=hours)

        if key not in self._storage:
            return []

        # Filter and keep only recent entries
        all_values = self._storage[key]
        recent = [(ts, val) for ts, val in all_values if ts >= cutoff_time]

        # Update storage with only recent entries (cleanup old data)
        if len(recent) != len(all_values):
            removed = len(all_values) - len(recent)
            self._storage[key] = recent
            logger.debug(f"Cleaned up {removed} old entries for key={key}")

            # Remove key if empty
            if not recent:
                del self._storage[key]

        logger.debug(f"Retrieved {len(recent)} recent entries for key={key} within {hours} hours")
        return recent

    def count_recent(self, key: str, hours: int) -> int:
        """
        Count values for a key within the last N hours.

        Args:
            key: Storage key
            hours: Number of hours to look back

        Returns:
            Count of entries within the time window
        """
        return len(self.get_recent(key, hours))

    def get_all_keys(self) -> List[str]:
        """
        Get all keys in storage.

        Returns:
            List of all keys
        """
        return list(self._storage.keys())

    def clear(self, key: str = None) -> None:
        """
        Clear storage for a specific key or all keys.

        Args:
            key: Optional key to clear (if None, clears all)
        """
        if key is None:
            self._storage.clear()
            logger.debug("Cleared all storage")
        else:
            if key in self._storage:
                del self._storage[key]
                logger.debug(f"Cleared storage for key={key}")

    def get_stats(self) -> Dict[str, int]:
        """
        Get storage statistics.

        Returns:
            Dictionary with statistics
        """
        total_entries = sum(len(values) for values in self._storage.values())
        return {"total_keys": len(self._storage), "total_entries": total_entries}
