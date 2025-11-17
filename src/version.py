import logging
import tomllib
from pathlib import Path

logger = logging.getLogger(__name__)


def get_version() -> str:
    """
    Get the project version from pyproject.toml.

    Returns:
        Version string or "unknown" if unable to read
    """
    try:
        pyproject_path = Path(__file__).parent.parent / "pyproject.toml"

        if not pyproject_path.exists():
            logger.warning("pyproject.toml not found")
            return "unknown"

        with open(pyproject_path, "rb") as f:
            pyproject_data = tomllib.load(f)

        version = pyproject_data.get("project", {}).get("version", "unknown")
        return version

    except Exception as e:
        logger.error(f"Failed to read version: {e}")
        return "unknown"


__version__ = get_version()
