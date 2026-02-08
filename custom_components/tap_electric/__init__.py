import logging
from datetime import timedelta

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

from .api import TapElectricAPI
from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Tap Electric via config entry."""
    api = TapElectricAPI(entry.data["api_key"])
    
    # Sla de API instantie op zodat andere platformen (zoals de slider) erbij kunnen
    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN]["api_instance"] = api
    
    async def async_update_data():
        """Data ophalen van de API."""
        chargers = await api.get_chargers()
        sessions = await api.get_active_sessions()
        return {"chargers": chargers, "sessions": sessions}

    coordinator = DataUpdateCoordinator(
        hass,
        _LOGGER,
        name="Tap Electric",
        update_method=async_update_data,
        update_interval=timedelta(seconds=30),
    )

    await coordinator.async_config_entry_first_refresh()
    hass.data[DOMAIN][entry.entry_id] = coordinator

    # Start de sensoren en de slider
    await hass.config_entries.async_forward_entry_setups(entry, ["sensor", "number"])
    return True

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload een config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, ["sensor", "number"])
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)
    return unload_ok
