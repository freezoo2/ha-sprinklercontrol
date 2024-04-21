"""Home Assistant component for accessing the Sprinkler Control API.
The number component allows control of charging current.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import cast, Union

from homeassistant.components.number import NumberEntity, NumberEntityDescription
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import PlatformNotReady
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from . import InvalidAuth, SprinklerControlCoordinator, SprinklerControlEntity
from .const import (    
    CONF_IP,
    WATERING_TIME_KEY,
    WATERING_MAX_TIME,
    WATERING_STATE,
    DOMAIN,
)


@dataclass
class SprinklerControlNumberEntityDescription(NumberEntityDescription):
    """Describes SprinklerControl number entity."""

NUMBER_TYPES: dict[str, SprinklerControlNumberEntityDescription] = {
    WATERING_TIME_KEY: SprinklerControlNumberEntityDescription(
        key=WATERING_TIME_KEY,
        name="Time in seconds for sprinkler to be activated",
    ),
    WATERING_STATE: SprinklerControlNumberEntityDescription(
        key=WATERING_STATE,
        name="Current status of sprinkler",
    ),

}


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback) -> None:
    """Create SprinklerControl number entities in HASS."""
    coordinator: SprinklerControlCoordinator = hass.data[DOMAIN][entry.entry_id]
    # Add number component:
    async_add_entities(
        [
            SprinklerControlNumber(coordinator, entry, description)
            for ent in coordinator.data
            if (description := NUMBER_TYPES.get(ent))
        ]
    )


class SprinklerControlNumber(SprinklerControlEntity, NumberEntity):
    """Representation of the SprinklerControl API."""

    entity_description: SprinklerControlNumberEntityDescription

    def __init__(
        self,
        coordinator: SprinklerControlCoordinator,
        entry: ConfigEntry,
        description: SprinklerControlNumberEntityDescription,
    ) -> None:
        """Initialize a SprinklerControl number entity."""
        super().__init__(coordinator)
        self.entity_description = description
        self._coordinator = coordinator
        self._attr_name = f"{entry.title} {description.name}"
        #self._attr_unique_id = f"{description.key}-{coordinator.data[CONF_IP]}"
        self._attr_unique_id = f"{description.key}-1111"        

    @property
    def native_max_value(self) -> float:
        """Return the maximum available current."""
        return WATERING_MAX_TIME

    @property
    def native_min_value(self) -> float:        
        return 0

    @property
    def native_value(self) -> float | None:
        """Return the value of the entity."""
        #return cast(
        #    Union [float,None], self._coordinator.data[WATERING_MAX_TIME]
        #)
        return self._coordinator.data[WATERING_STATE]

    async def async_set_native_value(self, value: float) -> None:
        """Set the value of the entity."""
        await self._coordinator.async_start_watering(value)