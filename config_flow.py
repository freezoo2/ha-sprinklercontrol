"""Config flow for SprinklerControl integration."""
from __future__ import annotations

from collections.abc import Mapping
from typing import Any

import voluptuous as vol
from .sprinklercontrol import SprinklerControl

from homeassistant import config_entries, core
from homeassistant.helpers import selector
from homeassistant.const import CONF_PASSWORD, CONF_USERNAME
from homeassistant.data_entry_flow import FlowResult

from . import InvalidAuth, SprinklerControlCoordinator
from .const import CONF_IP, DOMAIN

COMPONENT_DOMAIN = DOMAIN

STEP_USER_DATA_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_IP): str,
    }
)


async def validate_input(hass: core.HomeAssistant, data: dict[str, Any]) -> dict[str, str]:
    """Validate the user input allows to connect.

    Data has the keys from STEP_USER_DATA_SCHEMA with values provided by the user.
    """
    sc = SprinklerControl(data[CONF_IP])
    sc_coordinator = SprinklerControlCoordinator(data[CONF_IP], sc, hass)

    await sc_coordinator.async_validate_input()

    # Return info that you want to store in the config entry.
    return {"title": "Sprinkler Control"}


class ConfigFlow(config_entries.ConfigFlow, domain=COMPONENT_DOMAIN):
    """Handle a config flow for SprinklerControl."""

    def __init__(self) -> None:
        """Start the SprinklerControl config flow."""
#        self._reauth_entry: config_entries.ConfigEntry | None = None
        self._temp_IP = None

    async def async_step_user(self, user_input: dict[str, Any] | None = None) -> FlowResult:
        """Handle the initial step."""
        if user_input is None:
            return self.async_show_form(
                step_id="user",
                data_schema=STEP_USER_DATA_SCHEMA,
            )

        errors = {}

        try:
            if CONF_IP in user_input:
                info = await validate_input(self.hass, user_input)
                return self.async_create_entry(title=info["title"], data={CONF_IP: user_input[CONF_IP]})
        except ConnectionError:
            errors["base"] = "cannot_connect"

        return self.async_show_form(
            step_id="user",
            data_schema=STEP_USER_DATA_SCHEMA,
            errors=errors,
        )