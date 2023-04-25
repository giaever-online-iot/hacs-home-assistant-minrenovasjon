from homeassistant.exceptions import HomeAssistantError


class AddressNotFound(HomeAssistantError):
    """Error to indicate address(es) is not found"""


class FractionsNotFound(HomeAssistantError):
    """Error to indicate fractions is not found"""


class CannotConnect(HomeAssistantError):
    """Error to indicate we cannot connect."""


class InvalidParameters(HomeAssistantError):
    """Error to indicate there is invalid auth."""
