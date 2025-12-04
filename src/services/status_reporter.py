import asyncio
import logging

from aiogram import Bot

from src.config import config
from src.i18n import get_translation as _
from src.utils.connection_tracker import ConnectionLossTracker
from src.utils.timezone_helper import get_current_timestamp

logger = logging.getLogger(__name__)

COUNTRIES_DICT = {
    "XX": "🏴‍☠️ Unknown",
    "AF": "🇦🇫 Afghanistan",
    "AL": "🇦🇱 Albania",
    "DZ": "🇩🇿 Algeria",
    "AD": "🇦🇩 Andorra",
    "AO": "🇦🇴 Angola",
    "AG": "🇦🇬 Antigua and Barbuda",
    "AR": "🇦🇷 Argentina",
    "AM": "🇦🇲 Armenia",
    "AU": "🇦🇺 Australia",
    "AT": "🇦🇹 Austria",
    "AZ": "🇦🇿 Azerbaijan",
    "BS": "🇧🇸 Bahamas",
    "BH": "🇧🇭 Bahrain",
    "BD": "🇧🇩 Bangladesh",
    "BB": "🇧🇧 Barbados",
    "BY": "🇧🇾 Belarus",
    "BE": "🇧🇪 Belgium",
    "BZ": "🇧🇿 Belize",
    "BJ": "🇧🇯 Benin",
    "BT": "🇧🇹 Bhutan",
    "BO": "🇧🇴 Bolivia",
    "BA": "🇧🇦 Bosnia and Herzegovina",
    "BW": "🇧🇼 Botswana",
    "BR": "🇧🇷 Brazil",
    "BN": "🇧🇳 Brunei",
    "BG": "🇧🇬 Bulgaria",
    "BF": "🇧🇫 Burkina Faso",
    "BI": "🇧🇮 Burundi",
    "KH": "🇰🇭 Cambodia",
    "CM": "🇨🇲 Cameroon",
    "CA": "🇨🇦 Canada",
    "CV": "🇨🇻 Cape Verde",
    "CF": "🇨🇫 Central African Republic",
    "TD": "🇹🇩 Chad",
    "CL": "🇨🇱 Chile",
    "CN": "🇨🇳 China",
    "HK": "🇭🇰 Hong Kong",
    "CO": "🇨🇴 Colombia",
    "KM": "🇰🇲 Comoros",
    "CG": "🇨🇬 Congo",
    "CR": "🇨🇷 Costa Rica",
    "HR": "🇭🇷 Croatia",
    "CU": "🇨🇺 Cuba",
    "CY": "🇨🇾 Cyprus",
    "CZ": "🇨🇿 Czech Republic",
    "DK": "🇩🇰 Denmark",
    "DJ": "🇩🇯 Djibouti",
    "DM": "🇩🇲 Dominica",
    "DO": "🇩🇴 Dominican Republic",
    "EC": "🇪🇨 Ecuador",
    "EG": "🇪🇬 Egypt",
    "SV": "🇸🇻 El Salvador",
    "GQ": "🇬🇶 Equatorial Guinea",
    "ER": "🇪🇷 Eritrea",
    "EE": "🇪🇪 Estonia",
    "ET": "🇪🇹 Ethiopia",
    "FJ": "🇫🇯 Fiji",
    "FI": "🇫🇮 Finland",
    "FR": "🇫🇷 France",
    "GA": "🇬🇦 Gabon",
    "GM": "🇬🇲 Gambia",
    "GE": "🇬🇪 Georgia",
    "DE": "🇩🇪 Germany",
    "GH": "🇬🇭 Ghana",
    "GR": "🇬🇷 Greece",
    "GD": "🇬🇩 Grenada",
    "GT": "🇬🇹 Guatemala",
    "GN": "🇬🇳 Guinea",
    "GW": "🇬🇼 Guinea-Bissau",
    "GY": "🇬🇾 Guyana",
    "HT": "🇭🇹 Haiti",
    "HN": "🇭🇳 Honduras",
    "HU": "🇭🇺 Hungary",
    "IS": "🇮🇸 Iceland",
    "IN": "🇮🇳 India",
    "ID": "🇮🇩 Indonesia",
    "IR": "🇮🇷 Iran",
    "IQ": "🇮🇶 Iraq",
    "IE": "🇮🇪 Ireland",
    "IL": "🇮🇱 Israel",
    "IT": "🇮🇹 Italy",
    "JM": "🇯🇲 Jamaica",
    "JP": "🇯🇵 Japan",
    "JO": "🇯🇴 Jordan",
    "KZ": "🇰🇿 Kazakhstan",
    "KE": "🇰🇪 Kenya",
    "KI": "🇰🇮 Kiribati",
    "KP": "🇰🇵 North Korea",
    "KR": "🇰🇷 South Korea",
    "KW": "🇰🇼 Kuwait",
    "KG": "🇰🇬 Kyrgyzstan",
    "LA": "🇱🇦 Laos",
    "LV": "🇱🇻 Latvia",
    "LB": "🇱🇧 Lebanon",
    "LS": "🇱🇸 Lesotho",
    "LR": "🇱🇷 Liberia",
    "LY": "🇱🇾 Libya",
    "LI": "🇱🇮 Liechtenstein",
    "LT": "🇱🇹 Lithuania",
    "LU": "🇱🇺 Luxembourg",
    "MG": "🇲🇬 Madagascar",
    "MW": "🇲🇼 Malawi",
    "MY": "🇲🇾 Malaysia",
    "MV": "🇲🇻 Maldives",
    "ML": "🇲🇱 Mali",
    "MT": "🇲🇹 Malta",
    "MH": "🇲🇭 Marshall Islands",
    "MR": "🇲🇷 Mauritania",
    "MU": "🇲🇺 Mauritius",
    "MX": "🇲🇽 Mexico",
    "FM": "🇫🇲 Micronesia",
    "MD": "🇲🇩 Moldova",
    "MC": "🇲🇨 Monaco",
    "MN": "🇲🇳 Mongolia",
    "ME": "🇲🇪 Montenegro",
    "MA": "🇲🇦 Morocco",
    "MZ": "🇲🇿 Mozambique",
    "MM": "🇲🇲 Myanmar",
    "NA": "🇳🇦 Namibia",
    "NR": "🇳🇷 Nauru",
    "NP": "🇳🇵 Nepal",
    "NL": "🇳🇱 Netherlands",
    "NZ": "🇳🇿 New Zealand",
    "NI": "🇳🇮 Nicaragua",
    "NE": "🇳🇪 Niger",
    "NG": "🇳🇬 Nigeria",
    "NO": "🇳🇴 Norway",
    "OM": "🇴🇲 Oman",
    "PK": "🇵🇰 Pakistan",
    "PW": "🇵🇼 Palau",
    "PA": "🇵🇦 Panama",
    "PG": "🇵🇬 Papua New Guinea",
    "PY": "🇵🇾 Paraguay",
    "PE": "🇵🇪 Peru",
    "PH": "🇵🇭 Philippines",
    "PL": "🇵🇱 Poland",
    "PT": "🇵🇹 Portugal",
    "QA": "🇶🇦 Qatar",
    "RO": "🇷🇴 Romania",
    "RU": "🇷🇺 Russia",
    "RW": "🇷🇼 Rwanda",
    "KN": "🇰🇳 Saint Kitts and Nevis",
    "LC": "🇱🇨 Saint Lucia",
    "VC": "🇻🇨 Saint Vincent and the Grenadines",
    "WS": "🇼🇸 Samoa",
    "SM": "🇸🇲 San Marino",
    "ST": "🇸🇹 Sao Tome and Principe",
    "SA": "🇸🇦 Saudi Arabia",
    "SN": "🇸🇳 Senegal",
    "RS": "🇷🇸 Serbia",
    "SC": "🇸🇨 Seychelles",
    "SL": "🇸🇱 Sierra Leone",
    "SG": "🇸🇬 Singapore",
    "SK": "🇸🇰 Slovakia",
    "SI": "🇸🇮 Slovenia",
    "SB": "🇸🇧 Solomon Islands",
    "SO": "🇸🇴 Somalia",
    "ZA": "🇿🇦 South Africa",
    "SS": "🇸🇸 South Sudan",
    "ES": "🇪🇸 Spain",
    "LK": "🇱🇰 Sri Lanka",
    "SD": "🇸🇩 Sudan",
    "SR": "🇸🇷 Suriname",
    "SE": "🇸🇪 Sweden",
    "CH": "🇨🇭 Switzerland",
    "SY": "🇸🇾 Syria",
    "TW": "🇹🇼 Taiwan",
    "TJ": "🇹🇯 Tajikistan",
    "TZ": "🇹🇿 Tanzania",
    "TH": "🇹🇭 Thailand",
    "TL": "🇹🇱 Timor-Leste",
    "TG": "🇹🇬 Togo",
    "TO": "🇹🇴 Tonga",
    "TT": "🇹🇹 Trinidad and Tobago",
    "TN": "🇹🇳 Tunisia",
    "TR": "🇹🇷 Turkey",
    "TM": "🇹🇲 Turkmenistan",
    "TV": "🇹🇻 Tuvalu",
    "UG": "🇺🇬 Uganda",
    "UA": "🇺🇦 Ukraine",
    "AE": "🇦🇪 United Arab Emirates",
    "GB": "🇬🇧 United Kingdom",
    "US": "🇺🇸 United States",
    "UY": "🇺🇾 Uruguay",
    "UZ": "🇺🇿 Uzbekistan",
    "VU": "🇻🇺 Vanuatu",
    "VA": "🇻🇦 Vatican City",
    "VE": "🇻🇪 Venezuela",
    "VN": "🇻🇳 Vietnam",
    "YE": "🇾🇪 Yemen",
    "ZM": "🇿🇲 Zambia",
    "ZW": "🇿🇼 Zimbabwe",
}


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
        stats_lines = self.connection_tracker.get_statistics_lines()
        if not stats_lines:
            logger.debug("No statistics to report")
            return

        stats_dict = self.connection_tracker.get_statistics()
        provider_stats = self.connection_tracker.get_provider_statistics()
        country_stats = self.connection_tracker.get_country_statistics()
        stats_formatted = "\n".join([line for line in stats_lines])

        message_parts = [
            f"<b>{_('connection-stats-title', hours=config.CONNECTION_LOSS_STATS_HOURS)}</b>",
            stats_formatted,
        ]

        if provider_stats:
            provider_lines = [
                f"<code>{provider}</code> - x{count}"
                for provider, count in sorted(provider_stats.items(), key=lambda x: (-x[1], x[0]))
            ]
            message_parts.append(f"\n<b>{_('provider-stats-title')}:</b>")
            message_parts.append("\n".join(provider_lines))

        if country_stats:
            country_lines = [
                f"<code>{COUNTRIES_DICT.get(country, country)}</code> - x{count}"
                for country, count in sorted(country_stats.items(), key=lambda x: (-x[1], x[0]))
            ]
            message_parts.append(f"\n<b>{_('country-stats-title')}:</b>")
            message_parts.append("\n".join(country_lines))

        total_count = sum(stats_dict.values())
        message_parts.append(f"\n<b>{_('total-stats-label')}:</b> x{total_count}")

        message_parts.append(f"\n<b>{_('message-header-time')}:</b> {get_current_timestamp()}")
        message = "\n".join(message_parts)

        try:
            await self.bot.send_message(
                chat_id=config.TELEGRAM_CHAT_ID,
                text=message,
                message_thread_id=int(config.TOPIC_STATUS),
            )
            logger.info("Status report sent")
        except Exception as e:
            logger.error(f"Failed to send status report: {e}", exc_info=True)
