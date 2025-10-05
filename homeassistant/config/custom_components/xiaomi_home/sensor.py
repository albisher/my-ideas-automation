"""Sensor support for Xiaomi Home integration."""
from __future__ import annotations

import logging
from typing import Any

from homeassistant.components.sensor import SensorEntity
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
    """Set up Xiaomi Home sensors based on a config entry."""
    coordinator = hass.data[DOMAIN][config_entry.entry_id]

    # Add sensors for device status
    sensors = [
        XiaomiDeviceSensor(coordinator, "connection_status", "Connection Status"),
        XiaomiDeviceSensor(coordinator, "ir_devices", "IR Devices Count"),
        XiaomiDeviceSensor(coordinator, "last_command", "Last IR Command"),
    ]
    
    async_add_entities(sensors)


class XiaomiDeviceSensor(SensorEntity):
    """Representation of a Xiaomi Device Sensor."""

    def __init__(self, coordinator, sensor_type: str, sensor_name: str) -> None:
        """Initialize the sensor."""
        self.coordinator = coordinator
        self._sensor_type = sensor_type
        self._attr_name = f"Xiaomi {sensor_name}"
        self._attr_unique_id = f"xiaomi_{sensor_type}"
        self._attr_device_info = {
            "identifiers": {(DOMAIN, f"xiaomi_{sensor_type}")},
            "name": f"Xiaomi {sensor_name}",
            "manufacturer": "Xiaomi",
            "model": "Smart Speaker with IR",
        }
        self._attr_native_value = self._get_sensor_value()

    def _get_sensor_value(self) -> str | int:
        """Get the sensor value based on type."""
        if self._sensor_type == "connection_status":
            return "Connected"
        elif self._sensor_type == "ir_devices":
            return 4  # Number of IR devices configured
        elif self._sensor_type == "last_command":
            return "None"
        return "Unknown"

    @property
    def native_value(self) -> str | int:
        """Return the state of the sensor."""
        return self._attr_native_value
