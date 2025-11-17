import logging
from typing import Dict, Any, Optional

import aiohttp

logger = logging.getLogger(__name__)


class IPGeolocationService:
    """Service for fetching IP geolocation data from ip-api.com."""

    # noinspection HttpUrlsUsage
    BASE_URL = "http://ip-api.com/json"

    @staticmethod
    async def get_location(ip: str) -> Optional[Dict[str, Any]]:
        """
        Fetch geolocation data for an IP address.

        Args:
            ip: IP address to lookup

        Returns:
            Dictionary with location data or None if lookup fails
        """
        try:
            params = {"fields": "status,country,countryCode,regionName,city,isp,query"}

            url = f"{IPGeolocationService.BASE_URL}/{ip}"

            async with aiohttp.ClientSession() as session:
                async with session.get(url, params=params, timeout=5) as response:
                    if response.status == 200:
                        data = await response.json()
                        if data.get("status") == "success":
                            return {
                                "country": data.get("country", "Unknown"),
                                "countryCode": data.get("countryCode", ""),
                                "regionName": data.get("regionName", ""),
                                "city": data.get("city", ""),
                                "isp": data.get("isp", ""),
                            }
                        else:
                            logger.warning(f"IP geolocation lookup failed for {ip}: {data}")
                            return None
                    else:
                        logger.error(f"IP geolocation API returned status {response.status}")
                        return None

        except aiohttp.ClientTimeout:
            logger.error(f"Timeout while fetching geolocation for IP {ip}")
            return None
        except Exception as e:
            logger.error(f"Error fetching geolocation for IP {ip}: {e}")
            return None
