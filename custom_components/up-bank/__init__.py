import logging
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from .up import UP
from .const import DOMAIN
from homeassistant.const import CONF_API_KEY

PLATFORMS: list[str] = ["sensor"]
_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = UP(entry.data[CONF_API_KEY])
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)

    return unload_ok