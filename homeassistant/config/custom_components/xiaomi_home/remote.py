"""Remote support for Xiaomi Home IR control."""
from __future__ import annotations

import logging
from typing import Any

from homeassistant.components.remote import RemoteEntity, RemoteEntityFeature
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
    """Set up Xiaomi Home remote based on a config entry."""
    coordinator = hass.data[DOMAIN][config_entry.entry_id]

    # Add remote for IR control
    async_add_entities([XiaomiIRRemote(coordinator)])


class XiaomiIRRemote(RemoteEntity):
    """Representation of a Xiaomi IR Remote."""

    _attr_name = "Xiaomi Smart Speaker IR"
    _attr_supported_features = RemoteEntityFeature.LEARN_COMMAND | RemoteEntityFeature.DELETE_COMMAND

    def __init__(self, coordinator) -> None:
        """Initialize the remote."""
        self.coordinator = coordinator
        self._attr_unique_id = "xiaomi_smart_speaker_ir"
        self._attr_device_info = {
            "identifiers": {(DOMAIN, "xiaomi_smart_speaker_ir")},
            "name": "Xiaomi Smart Speaker IR",
            "manufacturer": "Xiaomi",
            "model": "Smart Speaker with IR",
        }
        self._current_activity = None

    @property
    def current_activity(self) -> str | None:
        """Return the current activity."""
        return self._current_activity

    async def async_turn_on(self, activity: str | None = None, **kwargs: Any) -> None:
        """Turn on the device or specified activity."""
        if activity:
            self._current_activity = activity
            _LOGGER.info("Turning on activity: %s", activity)
        else:
            _LOGGER.info("Turning on Xiaomi IR Remote")

    async def async_turn_off(self, activity: str | None = None, **kwargs: Any) -> None:
        """Turn off the device or specified activity."""
        if activity:
            self._current_activity = None
            _LOGGER.info("Turning off activity: %s", activity)
        else:
            _LOGGER.info("Turning off Xiaomi IR Remote")

    async def async_send_command(self, command: list[str], **kwargs: Any) -> None:
        """Send a command."""
        _LOGGER.info("Sending IR command: %s", command)
        # Here you would implement the actual IR command sending
        # This is where you'd integrate with the Xiaomi API

    async def async_learn_command(self, **kwargs: Any) -> None:
        """Learn a command."""
        _LOGGER.info("Learning IR command")
        # Here you would implement command learning functionality

    async def async_delete_command(self, **kwargs: Any) -> None:
        """Delete a command."""
        _LOGGER.info("Deleting IR command")
        # Here you would implement command deletion functionality
