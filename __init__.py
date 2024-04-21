"""The SprinklerControl integration."""
from __future__ import annotations

from datetime import timedelta
from http import HTTPStatus
import logging
from typing import Any

import requests
from .sprinklercontrol import SprinklerControl

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryAuthFailed, HomeAssistantError
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.update_coordinator import (
    CoordinatorEntity,
    DataUpdateCoordinator,
    UpdateFailed,
)

from .const import (
    DOMAIN,
    CONF_IP,
    WATERING_STATE,
    SC_VERSION,
)

_LOGGER = logging.getLogger(__name__)

#PLATFORMS = [Platform.NUMBER, Platform.SWITCH]
PLATFORMS = [Platform.NUMBER]
UPDATE_INTERVAL = 30

class SprinklerControlCoordinator(DataUpdateCoordinator[dict[str, Any]]):
    """SprinklerControl Coordinator class."""

    def __init__(self, ipaddress: str, sc: SprinklerControl, hass: HomeAssistant) -> None:
        """Initialize."""
        self._ip = ipaddress
        self._sc = sc

        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=timedelta(seconds=UPDATE_INTERVAL),
        )

    def _confirm_ip(self) -> None:
        """Confirm there is a sprinkler controller at given IP and we have connectivity."""
        try:
            self._sc.current_state()

        except requests.exceptions.HTTPError as connection_error:
            raise ConnectionError from connection_error

    def _validate(self) -> None:
        """Confirm connectivity for Sprinkler controller API."""
        try:
            self._confirm_ip()
        except requests.exceptions.HTTPError as connection_error:
           raise ConnectionError from connection_error

    async def async_validate_input(self) -> None:
        """Get new sensor data for component."""
        await self.hass.async_add_executor_job(self._validate)

    def _get_data(self) -> dict[str, Any]:
        """Get new sensor data for component."""
        try:
            data: dict[str, Any] = {WATERING_STATE: self._sc.current_state()}
            return data
        except (
            ConnectionError,
            requests.exceptions.HTTPError,
        ) as connection_error:
            raise UpdateFailed from connection_error

    async def _async_update_data(self) -> dict[str, Any]:
        """Get new sensor data for component."""
        return await self.hass.async_add_executor_job(self._get_data)

    def _start_watering(self, seconds: int) -> None:
        """Start watering for number of seconds specified."""
        try:
            self._sc.start(seconds)
        except requests.exceptions.HTTPError as connection_error:
            raise ConnectionError from connection_error

    async def async_start_watering(self, seconds: float) -> None:
        """Start watering for number of seconds specified."""
        await self.hass.async_add_executor_job(
            self._start_watering, int(seconds)
        )
        await self.async_request_refresh()

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up SprinklerControl from a config entry."""
    sc = SprinklerControl(
        entry.data[CONF_IP],
    )
    sc_coordinator = SprinklerControlCoordinator(
        entry.data[CONF_IP],
        sc,
        hass,
    )

    try:
        await sc_coordinator.async_validate_input()

    except Exception as ex:
        raise ConfigEntryAuthFailed from ex

    await sc_coordinator.async_config_entry_first_refresh()

    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = sc_coordinator

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)

    return unload_ok


class InvalidAuth(HomeAssistantError):
    """Error to indicate there is invalid auth."""


class SprinklerControlEntity(CoordinatorEntity[SprinklerControlCoordinator]):
    """Defines a base SprinklerControl entity."""

    @property
    def device_info(self) -> DeviceInfo:
        """Return device information about this SprinklerControl device."""
        return DeviceInfo(
            identifiers={
                (
                    DOMAIN,
                    self.coordinator._ip
                )
            },
            name=f"SprinklerControl - {self.coordinator._ip}",
            manufacturer="JF",
            model="ESP32",
            sw_version=SC_VERSION,
        )