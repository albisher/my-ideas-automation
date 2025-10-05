"""Switch support for Xiaomi Home IR devices."""
from __future__ import annotations

import logging
from typing import Any

from homeassistant.components.switch import SwitchEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Xiaomi Home switches based on a config entry."""
    coordinator = hass.data[DOMAIN][config_entry.entry_id]

    # Add switches for common IR devices
    switches = [
        XiaomiIRSwitch(coordinator, "tv", "TV Power"),
        XiaomiIRSwitch(coordinator, "air_conditioner", "Air Conditioner"),
        XiaomiIRSwitch(coordinator, "fan", "Fan"),
        XiaomiIRSwitch(coordinator, "light", "Light"),
    ]
    
    async_add_entities(switches)


class XiaomiIRSwitch(SwitchEntity):
    """Representation of a Xiaomi IR Switch."""

    def __init__(self, coordinator, device_type: str, device_name: str) -> None:
        """Initialize the switch."""
        self.coordinator = coordinator
        self._device_type = device_type
        self._attr_name = f"Xiaomi IR {device_name}"
        self._attr_unique_id = f"xiaomi_ir_{device_type}"
        self._attr_device_info = {
            "identifiers": {(DOMAIN, f"xiaomi_ir_{device_type}")},
            "name": f"Xiaomi IR {device_name}",
            "manufacturer": "Xiaomi",
            "model": "Smart Speaker with IR",
        }
        self._is_on = False

    @property
    def is_on(self) -> bool:
        """Return true if the switch is on."""
        return self._is_on

    async def async_turn_on(self, **kwargs: Any) -> None:
        """Turn the switch on."""
        self._is_on = True
        _LOGGER.info("Turning on %s via IR", self._device_type)
        # Here you would implement the actual IR command sending
        # This would send the power on command for the specific device type

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Turn the switch off."""
        self._is_on = False
        _LOGGER.info("Turning off %s via IR", self._device_type)
        # Here you would implement the actual IR command sending
        # This would send the power off command for the specific device type
