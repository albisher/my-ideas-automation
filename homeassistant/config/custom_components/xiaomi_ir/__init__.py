"""
Xiaomi IR Remote Integration
This integration bypasses the token requirement and uses direct UDP communication
"""

import logging
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .custom_remote import XiaomiIRRemote

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the Xiaomi IR Remote integration."""
    _LOGGER.info("Setting up Xiaomi IR Remote integration")
    
    # Get the host from the config entry
    host = config_entry.data.get("host", "192.168.68.62")
    
    # Create the remote entity
    remote = XiaomiIRRemote(host)
    
    # Add the entity
    async_add_entities([remote], True)
    
    _LOGGER.info("Xiaomi IR Remote integration setup complete")
