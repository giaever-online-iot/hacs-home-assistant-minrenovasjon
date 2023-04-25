"""Config flow for MinRenovasjon integration."""
from __future__ import annotations

import logging
import voluptuous as vol

from homeassistant import config_entries
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResult
from homeassistant.helpers.selector import selector

from typing import Any, Literal

from . import const, MinRenovasjonApi, exceptions

_LOGGER = logging.getLogger(__name__)

STEP_ADDRESS_SCHEMA = vol.Schema(
    {
        vol.Required(
            "street_address", description={"suggested_value", "E.g Kirkegata X"}
        ): str
    }
)

STEP_SELECT_ADDRESS_SCHEMA = vol.Schema({vol.Required("addresses"): list[Any]})


class MinRenovasjonHub:
    """Placeholder class to make tests pass."""

    def __init__(self, hass) -> None:
        self.__api = MinRenovasjonApi(hass)

    async def get_households(
        self, street_address: str
    ) -> list[dict[str, Any]] | Literal[False]:
        """Docstring"""

        return await self.__api.query(
            const.URL_SEARCH_HOUSEHOLD.format(street_address=street_address),
            selector="adresser",
        )

    async def get_fractions(self, address: dict[str, Any]) -> list[dict[str, str]]:
        """Docstring"""

        municipality_code = address.get("kommunenummer", False)

        if not municipality_code:
            raise exceptions.InvalidParameters(
                "Expected municipality-code (kommunenummer) to be in the address-dictionary: {}".format(
                    address
                )
            )
        return await self.__api.query(
            const.URL_FRACTIONS,
            {
                const.KOMMUNE_NUMMER: municipality_code,
                const.APP_KEY: const.APP_KEY_VALUE,
            },
        )

    async def authenticate(self, address: str, house_number: str) -> bool:
        """Test if we can authenticate with the host."""
        return True


async def get_addresses(hass: HomeAssistant, address: str) -> list[dict[str, Any]]:
    """Docstring"""
    _LOGGER.debug("Lookup address for given address: %s", address)

    lookup = await MinRenovasjonHub(hass).get_households(address)

    if not lookup:
        raise exceptions.AddressNotFound("Address not found")

    _LOGGER.debug("Found addressses: %s", lookup)

    return lookup


async def get_fractions_for_address(
    hass: HomeAssistant, address: dict[str, Any]
) -> list[dict[str, str]]:
    """Docstring"""
    _LOGGER.debug("Lookup fractions for address: %s", address)

    lookup = await MinRenovasjonHub(hass).get_fractions(address)

    if not lookup:
        raise exceptions.FractionsNotFound(lookup)

    return lookup


class ConfigFlow(config_entries.ConfigFlow, domain=const.DOMAIN):
    """Handle a config flow for MinRenovasjon."""

    VERSION = 1

    def __init__(self) -> None:
        self.__addresses: list[dict[str, Any]] = []
        self.__selections: dict[str, Any] = {
            "address": None,
            "fractions": None,
        }

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        errors: dict[str, str] = {}

        _LOGGER.info("HELLO FROM minren")

        if user_input is not None:
            try:
                self.__addresses = await get_addresses(
                    self.hass, user_input["street_address"]
                )
                return await self.async_step_select_address()
            except exceptions.CannotConnect as err:
                _LOGGER.exception(err)
                errors["base"] = "cannot_connect"
            except exceptions.AddressNotFound as err:
                _LOGGER.exception(err)
                errors["base"] = "invalid_address"
            except Exception as err:  # pylint: disable=broad-except
                _LOGGER.exception(err)
                errors["base"] = "unknown"

        return self.async_show_form(
            step_id="user",
            data_schema=STEP_ADDRESS_SCHEMA,
            errors=errors,
        )

    async def async_step_select_address(
        self, address: dict[str, str] | None = None
    ) -> FlowResult:
        """Doc"""
        errors: dict[str, str] = {}
        _LOGGER.debug("List addresses to user")

        if address is not None:
            _LOGGER.debug("Selected address: %s", address)

            address_index = int(address.get("select_address", -1))

            if address_index < 0:
                errors["base"] = "select_one_address"
            else:
                _address = self.__addresses[address_index]
                _LOGGER.debug(
                    "Found address(es) with the selected address: %s", _address
                )

                self.__selections.update({"address": _address})

                return await self.async_step_select_fractions()

        address_options = [
            {
                "value": str(self.__addresses.index(addr)),
                "label": addr.get("adressetekst", "-unknown-"),
            }
            for addr in self.__addresses
        ]

        _LOGGER.debug("Address options %s", address_options)

        return self.async_show_form(
            step_id="select_address",
            data_schema=vol.Schema(
                {"select_address": selector({"select": {"options": address_options}})}
            ),
            errors=errors,
        )

    async def async_step_select_fractions(
        self, fractions: dict[str, list[dict[str, Any]]] | None = None
    ):
        """Docstring"""

        errors = {}
        address = self.__selections.get("address")
        if address is None:
            raise RuntimeError("Missing address")

        fraction_options = []
        try:
            _fractions = await get_fractions_for_address(self.hass, address)

            fraction_options = [
                {"value": str(fraction.get("Id")), "label": fraction.get("Navn")}
                for fraction in _fractions
            ]

            if fractions is not None:
                selected_fractions = fractions.get("select_fractions")
                _LOGGER.debug("SELECTED %s", selected_fractions)

                if selected_fractions is None or len(selected_fractions) == 0:
                    selected_fractions = [
                        int(fraction.get("value", 0)) for fraction in fraction_options
                    ]
                else:
                    selected_fractions = [
                        int(fraction.get("value", 0))
                        for fraction in fraction_options
                        if fraction.get("value") in selected_fractions
                    ]

                selected_fractions = [
                    {
                        "id": int(fraction.get("Id", 0)),
                        "type": fraction.get("Navn", "Unknown"),
                        "icon": fraction.get("Ikon", None),
                    }
                    for fraction in _fractions
                    if fraction.get("Id") in selected_fractions
                ]

                _LOGGER.debug("Selected fractions: %s", selected_fractions)
                self.__selections.update({"fractions": selected_fractions})

                # self.__selections.update({'fractions': selected_fractions})
                return self.async_create_entry(
                    title=address.get("adressetekst"),
                    data=self.__selections,
                    description="MinRenovasjon for «{}»".format(
                        address.get("adressetekst")
                    ),
                )
        except exceptions.CannotConnect as err:
            _LOGGER.exception(err)
            errors["base"] = "cannot_connect"
        except exceptions.FractionsNotFound as err:
            _LOGGER.exception(err)
            errors["base"] = "fractions_not_found"
        except Exception as err:  # pylint: disable=broad-except
            _LOGGER.exception(err)
            errors["base"] = "unknown"

        return self.async_show_form(
            step_id="select_fractions",
            data_schema=vol.Schema(
                {
                    "select_fractions": selector(
                        {"select": {"options": fraction_options, "multiple": True}}
                    )
                }
            ),
            errors={},
        )
