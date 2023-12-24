"""The MinRenovasjon integration."""
from __future__ import annotations

import logging
import urllib.parse

from typing import Any, Literal, cast

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant

from . import const

# TODO List the platforms that you want to support.
# For your initial PR, limit it to 1 platform.
PLATFORMS: list[Platform] = [Platform.CALENDAR, Platform.BINARY_SENSOR]
_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up MinRenovasjon from a config entry."""

    hass.data.setdefault(const.DOMAIN, {})

    _LOGGER.debug("ENTRY DATA: %s %s", entry.data, entry.entry_id)

    hass.data[const.DOMAIN][entry.entry_id] = MinRenovasjonApi(hass)

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    if unload_ok := await hass.config_entries.async_unload_platforms(entry, PLATFORMS):
        hass.data[const.DOMAIN].pop(entry.entry_id)

    return unload_ok


from homeassistant.helpers.aiohttp_client import async_get_clientsession
from .exceptions import CannotConnect, InvalidParameters
import aiohttp


class MinRenovasjonApi:
    def __init__(self, hass: HomeAssistant):
        self.__hass = hass
        self.__queries: dict[str, Any] = {}

    def __create_param(self, param: dict[str, str], value: str | int) -> dict[str, str]:
        return {list(param.keys())[0]: list(param.values())[0].format(value)}

    def build_calendar_url_from_address(self, address: dict[str, Any]) -> str:
        url = urllib.parse.urlparse(const.URL_CALENDAR)

        query = {}

        if street_name := address.get("adressenavn", False):
            query.update(
                self.__create_param(
                    const.URL_CALENDAR_STREET_NAME,
                    street_name,
                )
            )

        if street_code := address.get("adressekode", False):
            query.update(
                self.__create_param(const.URL_CALENDAR_STREET_CODE, street_code)
            )

        if house_number := address.get("nummer", False):
            query.update(
                self.__create_param(const.URL_CALENDAR_HOUSE_NUMBER, house_number)
            )

        return url._replace(query=urllib.parse.urlencode(query)).geturl()

    def get_cached_calendar_query_for_url(
        self, url: str
    ) -> list[dict[str, Any]] | Literal[False]:
        if result := self.__queries.get(url, False):
            _LOGGER.debug("Found result for url: %s => %s", url, result)
            return cast(list[dict[str, Any]], result)

        return False

    async def query(
        self, url: str, headers: dict[str, Any] = {}, selector: str | None = None
    ):
        session = async_get_clientsession(self.__hass)

        if url.startswith('https://komteksky'):
            url = const.URL_PROXY.format(urllib.parse.quote(url))

        _LOGGER.info("URL:%s", url)

        async with session.get(
            url, headers=headers, timeout=aiohttp.ClientTimeout(total=60)
        ) as req:
            req.raise_for_status()

            try:
                res = await req.json()
            except Exception as err:
                _LOGGER.exception(err)
                raise CannotConnect(
                    "Cannot connect: {}, selector={} headers={}".format(
                        url, selector, headers
                    )
                ) from err
            else:
                if selector:
                    if selector not in res:
                        raise InvalidParameters(
                            "Missing selector={} in res ({})".format(selector, res)
                        )

                    res = res.get(selector)

                _LOGGER.debug("URL: %s, returned: %s", url, res)

                self.__queries[url] = res
                return res
