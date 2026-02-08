import logging
from homeassistant.components.number import NumberEntity, NumberDeviceClass
from homeassistant.const import UnitOfElectricCurrent
from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass, entry, async_add_entities):
    """Stel de Tap Electric number entities (sliders) in."""
    api = hass.data[DOMAIN][entry.entry_id]
    
    # Haal alle laders op die onder jouw account vallen
    chargers = await api.get_chargers()
    
    entities = []
    for charger in chargers:
        # We maken voor elke lader een Ampère-slider aan
        entities.append(TapChargingLimitNumber(api, charger))
    
    async_add_entities(entities, update_before_add=True)

class TapChargingLimitNumber(NumberEntity):
    """Representatie van de laadstroom limiet slider."""

    def __init__(self, api, charger):
        """Initialiseer de slider."""
        self._api = api
        self._charger = charger
        self._charger_id = charger["id"]
        
        # Naamgeving in Home Assistant
        self._attr_name = f"Laadstroom Limiet {charger.get('name', self._charger_id)}"
        self._attr_unique_id = f"tap_limit_{self._charger_id}"
        
        # Instellingen van de slider
        self._attr_device_class = NumberDeviceClass.CURRENT
        self._attr_native_unit_of_measurement = UnitOfElectricCurrent.AMPERE
        self._attr_native_min_value = 6.0
        self._attr_native_max_value = 32.0  # Je kunt dit aanpassen naar 16.0 als je een kleine aansluiting hebt
        self._attr_native_step = 1.0
        
        # Beginwaarde (wordt later bijgewerkt via de API indien mogelijk)
        self._attr_native_value = 16.0

    async def async_set_native_value(self, value: float) -> None:
        """Update de laadstroom op de lader via de Tap API."""
        _LOGGER.debug("Instellen van laadstroom naar %s Ampère voor %s", value, self._charger_id)
        
        success = await self._api.set_charging_limit(self._charger_id, value)
        
        if success:
            self._attr_native_value = value
            self.async_write_ha_state()
        else:
            _LOGGER.error("Fout bij het instellen van de laadstroom limiet voor %s", self._charger_id)

    @property
    def device_info(self):
        """Koppel deze slider aan het lader-apparaat in HA."""
        return {
            "identifiers": {(DOMAIN, self._charger_id)},
            "name": self._charger.get('name', "Tap Lader"),
            "manufacturer": "Tap Electric",
            "model": self._charger.get('model', "OCPP Charger"),
        }
