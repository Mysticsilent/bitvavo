"""Initialisatie van de Bitvavo integratie."""

import logging
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

_LOGGER = logging.getLogger(__name__)
DOMAIN = "bitvavo"

async def async_setup(hass: HomeAssistant, config: dict):
    """Setup vanuit configuration.yaml (optioneel)."""
    hass.data.setdefault(DOMAIN, {})
    return True

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Setup de integratie via een config entry (toevoegen via de UI)."""
    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = entry.data

    # Correcte manier in nieuwere versies van Home Assistant
    await hass.config_entries.async_forward_entry_setups(entry, ["sensor"])
    return True

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Verwijder de integratie netjes."""
    unload_ok = all(
        await hass.config_entries.async_unload_platforms(entry, ["sensor"])
    )
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)
    return unload_ok
