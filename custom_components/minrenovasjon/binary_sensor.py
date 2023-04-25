from __future__ import annotations


import logging

# import urllib.parse

from datetime import datetime

from homeassistant import config_entries, core
from homeassistant.components.binary_sensor import BinarySensorEntity

from homeassistant.util import dt

# from datetime import datetime
from typing import Any, Mapping

from . import const, MinRenovasjonApi

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: core.HomeAssistant,
    config_entry: config_entries.ConfigEntry,
    async_add_entities,
) -> None:
    """Docstring"""
    api: MinRenovasjonApi | None = hass.data[const.DOMAIN][config_entry.entry_id]

    if api is None:
        _LOGGER.error("Missing API class")
    else:
        async_add_entities(
            [
                MinRenovasjonBinarySensor(api, fraction, config_entry)
                for fraction in config_entry.data.get("fractions", [])
            ],
            update_before_add=True,
        )


class MinRenovasjonBinarySensor(BinarySensorEntity):
    """Docstring"""

    def __init__(
        self,
        api: MinRenovasjonApi,
        fraction: dict[str, str],
        config: config_entries.ConfigEntry,
    ) -> None:
        self.__api: MinRenovasjonApi = api
        self.__fraction: dict[str, str] = fraction
        self.__address: dict[str, Any] = config.data.get("address", [])
        self.__events: list[datetime] | None = None

    @property
    def extra_state_attributes(self) -> Mapping[str, Any] | None:
        orig = super().extra_state_attributes

        attr = {
            "icon": "mdi:{}".format(
                "trash-can" if self.get_on_event is None else "delete-restore",
            ),
            "icon-url": self.__fraction.get("icon"),
        }

        if self.__events is not None and len(self.__events) != 0:
            attr["start_time"] = self.__events[0].strftime(const.DATE_FORMAT)

        if orig is not None:
            attr.update(orig)

        return attr

    @property
    def name(self) -> str | None:
        # self.hass.config_entries
        return "{}: {}".format(
            self.__address.get("adressetekst"), self.__fraction.get("type")
        )

    @property
    def unique_id(self) -> str | None:
        return "{} {}".format(
            self.__address.get("adressetekst"), self.__fraction.get("type")
        )

    @property
    def get_on_event(self) -> datetime | None:
        for event in self.__events or []:
            if event.today() == datetime.today():
                return event

        return None

    @property
    def is_on(self) -> bool:
        return self.get_on_event is not None

    async def async_update(self) -> None:
        if result := self.__api.get_cached_calendar_query_for_url(
            self.__api.build_calendar_url_from_address(self.__address)
        ):
            for fraction in result:
                if int(fraction.get("FraksjonId", -1)) == self.__fraction.get("id"):
                    self.__events = [
                        dt.start_of_local_day(
                            datetime.strptime(date, const.DATE_FORMAT)
                        )
                        for date in fraction.get("Tommedatoer", [])
                    ]
        else:
            _LOGGER.debug(
                "Calendar entity not updated yet, waiting for refresh for address: %s",
                self.__address.get("adressetekst"),
            )
