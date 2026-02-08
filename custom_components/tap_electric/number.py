from homeassistant.components.number import NumberEntity, NumberDeviceClass
from homeassistant.const import UnitOfElectricCurrent
from .const import DOMAIN

async def async_setup_entry(hass, entry, async_add_entities):
    coordinator = hass.data[DOMAIN][entry.entry_id]
    # De api zit verstopt in de coordinator
    api = coordinator.hass.data[DOMAIN][entry.entry_id].update_method.__self__.api 
    # Makkelijker: we halen de api direct uit de coordinator setup
    
    # Omdat we de API ook nodig hebben voor acties, halen we die uit hass.data
    # Maar voor nu gebruiken we de laders uit de coordinator data
    entities = []
    for charger in coordinator.data.get("chargers", []):
        entities.append(TapChargingLimit(coordinator, charger))
    async_add_entities(entities)

class TapChargingLimit(NumberEntity):
    _attr_device_class = NumberDeviceClass.CURRENT
    _attr_native_unit_of_measurement = UnitOfElectricCurrent.AMPERE
    _attr_native_min_value = 6
    _attr_native_max_value = 32
    _attr_native_step = 1

    def __init__(self, coordinator, charger):
        self.coordinator = coordinator
        self.charger_id = charger["id"]
        self.charger_name = charger.get("name", f"Lader {self.charger_id[-4:]}")
        self._attr_name = f"{self.charger_name} Limiet"
        self._attr_unique_id = f"tap_limit_{self.charger_id}"
        self._attr_native_value = 16

    @property
    def device_info(self):
        return {
            "identifiers": {(DOMAIN, self.charger_id)},
            "name": self.charger_name,
            "manufacturer": "Tap Electric",
        }

    async def async_set_native_value(self, value):
        # We hebben de API nodig om te versturen. 
        # In de __init__.py hebben we de API niet in de coordinator gestopt. 
        # Laten we dat voor de zekerheid even fixen in __init__.py.
        api = self.coordinator.hass.data[DOMAIN]["api_instance"]
        await api.set_charging_limit(self.charger_id, value)
        self._attr_native_value = value
        self.async_write_ha_state()
