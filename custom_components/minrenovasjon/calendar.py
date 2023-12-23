from __future__ import annotations


import logging


from homeassistant import config_entries, core
from homeassistant.components.calendar import CalendarEntity, CalendarEvent
from homeassistant.util import dt

from datetime import datetime
from typing import Any

from . import const, MinRenovasjonApi

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: core.HomeAssistant,
    config_entry: config_entries.ConfigEntry,
    async_add_entities,
) -> None:
    api: MinRenovasjonApi | None = hass.data[const.DOMAIN][config_entry.entry_id]

    if api is None:
        _LOGGER.error("Missing API class")
    else:
        async_add_entities(
            [MinRenovasjonCalendar(api, config_entry)], update_before_add=True
        )


class MinRenovasjonCalendar(CalendarEntity):
    """Doc"""

    def __init__(
        self, api: MinRenovasjonApi, entry: config_entries.ConfigEntry
    ) -> None:
        self.__entry: config_entries.ConfigEntry = entry
        self.__address: dict[str, Any] = self.__entry.data.get("address", {})
        self.__fractions: list[dict[str, str]] = self.__entry.data.get("fractions", {})
        self.__events: list[CalendarEvent] = []
        self.__api = api

    @property
    def __get_street_address(self) -> str:
        return self.__address.get("adressetekst", "unknown")

    @property
    def event(self) -> CalendarEvent | None:
        return self.__events[0] if len(self.__events) > 0 else None

    @property
    def supported_features(self) -> int | None:
        return None

    @property
    def name(self) -> str:
        _LOGGER.debug("%s.name: %s", self.__class__, self.__get_street_address)
        return self.__get_street_address

    @property
    def unique_id(self) -> str:
        return self.__get_street_address

    async def async_get_events(
        self, hass: core.HomeAssistant, start_date: datetime, end_date: datetime
    ) -> list[CalendarEvent]:
        _events = []

        for event in self.__events:
            if start_date.date() <= event.start <= end_date.date():
                _events.append(event)
            elif end_date.date() >= event.end >= start_date.date():
                _events.append(event)

        return _events

    async def async_update(self) -> None:
        """Docstring"""

        try:
            events = await self.__api.query(
                self.__api.build_calendar_url_from_address(self.__address),
                headers={
                    const.KOMMUNE_NUMMER: self.__address.get("kommunenummer"),
                    const.APP_KEY: const.APP_KEY_VALUE,
                },
            )
        except Exception as err:
            _LOGGER.exception(err)
        else:
            self.__event_copy = self.__events
            self.__events = []
            for collection in events:
                fraction_id = int(collection.get("FraksjonId", -1))

                for fraction in self.__fractions:
                    if fraction.get("id") == fraction_id:
                        dates = collection.get("Tommedatoer", None)

                        for date in dates:
                            start = dt.start_of_local_day(
                                datetime.strptime(date, const.DATE_FORMAT)
                            )
                            self.__events.append(
                                CalendarEvent(
                                    start=start.date(),
                                    end=start.date(),
                                    summary=fraction.get("type", "Unknown fraction..."),
                                    location=self.__get_street_address,
                                )
                            )

                        self.__sort_by_start()

                if self.__events != self.__event_copy:
                    _LOGGER.debug("Events: %s", self.__events)

    def __sort_by_start(self) -> None:
        self.__events.sort(key=lambda x: x.start)
