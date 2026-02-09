import logging
from datetime import timedelta

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .api import TapElectricAPI
from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

# We voegen 'select' toe voor de fase-instelling
PLATFORMS: list[str] = ["sensor", "number", "switch", "select"]

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Tap Electric via config entry."""
    
    # Initialiseer de API
    api = TapElectricAPI(entry.data["api_key"])
    
    async def async_update_data():
        """Data ophalen van de API via de centrale get_data methode."""
        try:
            # We gebruiken nu de nieuwe gecombineerde methode uit api.py
            data = await api.get_data()
            
            if not data or "chargers" not in data:
                raise UpdateFailed("Geen geldige data ontvangen van de Tap API")
                
            _LOGGER.debug("Data succesvol ververst: %s chargers gevonden", len(data.get("chargers", [])))
            return data
            
        except Exception as err:
            _LOGGER.error("Fout bij ophalen data van Tap Electric: %s", err)
            raise UpdateFailed(f"Fout bij communicatie met API: {err}")

    # Maak de coordinator aan (ververst elke 30 seconden)
    coordinator = DataUpdateCoordinator(
        hass,
        _LOGGER,
        name="Tap Electric",
        update_method=async_update_data,
        update_interval=timedelta(seconds=30),
    )

    # Voeg de api instantie toe aan de coordinator zodat switches erbij kunnen
    coordinator.api = api

    # Eerste refresh doen
    await coordinator.async_config_entry_first_refresh()
    
    # Sla de coordinator centraal op
    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = coordinator

    # Start de platformen (sensor, number, switch, select)
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    
    return True

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload een config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)
    return unload_ok
