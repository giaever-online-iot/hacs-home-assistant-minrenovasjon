"""The MinRenovasjon integration."""
from __future__ import annotations

import logging
import urllib.parse

from . import const
from typing import Any, Literal, cast
from .exceptions import CannotConnect, InvalidParameters

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
import aiohttp

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

        params={}

        if url.startswith('https://komteksky'):
            params={
                'server': url
            }
            url = const.URL_PROXY 

        _LOGGER.debug("URL: %s, params=%s, header=%s", url, str(params), str(headers))

        async with aiohttp.ClientSession(headers=headers) as session:
            async with session.get(url=url, params=params) as req:
                try:
                    res = await req.json(encoding="UTF-8", content_type="text/html")
                except Exception as err:
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