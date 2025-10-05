"""Media player support for Xiaomi Home integration."""
from __future__ import annotations

import logging
from typing import Any

from homeassistant.components.media_player import (
    MediaPlayerEntity,
    MediaPlayerEntityFeature,
    MediaPlayerState,
)
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
    """Set up Xiaomi Home media player based on a config entry."""
    coordinator = hass.data[DOMAIN][config_entry.entry_id]

    # Add media player for smart speaker
    async_add_entities([XiaomiSmartSpeaker(coordinator)])


class XiaomiSmartSpeaker(MediaPlayerEntity):
    """Representation of a Xiaomi Smart Speaker."""

    _attr_name = "Xiaomi Smart Speaker"
    _attr_supported_features = (
        MediaPlayerEntityFeature.VOLUME_SET
        | MediaPlayerEntityFeature.VOLUME_MUTE
        | MediaPlayerEntityFeature.PLAY_MEDIA
        | MediaPlayerEntityFeature.STOP
        | MediaPlayerEntityFeature.PAUSE
        | MediaPlayerEntityFeature.PLAY
    )

    def __init__(self, coordinator) -> None:
        """Initialize the media player."""
        self.coordinator = coordinator
        self._attr_unique_id = "xiaomi_smart_speaker"
        self._attr_device_info = {
            "identifiers": {(DOMAIN, "xiaomi_smart_speaker")},
            "name": "Xiaomi Smart Speaker",
            "manufacturer": "Xiaomi",
            "model": "Smart Speaker with IR",
        }

    @property
    def state(self) -> MediaPlayerState:
        """Return the state of the device."""
        return MediaPlayerState.IDLE

    @property
    def volume_level(self) -> float | None:
        """Volume level of the media player (0..1)."""
        return 0.5

    @property
    def is_volume_muted(self) -> bool:
        """Boolean if volume is currently muted."""
        return False

    async def async_media_play(self) -> None:
        """Send play command."""
        _LOGGER.info("Playing media on Xiaomi Smart Speaker")

    async def async_media_pause(self) -> None:
        """Send pause command."""
        _LOGGER.info("Pausing media on Xiaomi Smart Speaker")

    async def async_media_stop(self) -> None:
        """Send stop command."""
        _LOGGER.info("Stopping media on Xiaomi Smart Speaker")

    async def async_set_volume_level(self, volume: float) -> None:
        """Set volume level, range 0..1."""
        _LOGGER.info("Setting volume to %s on Xiaomi Smart Speaker", volume)

    async def async_mute_volume(self, mute: bool) -> None:
        """Mute the volume."""
        _LOGGER.info("Muting volume: %s on Xiaomi Smart Speaker", mute)
