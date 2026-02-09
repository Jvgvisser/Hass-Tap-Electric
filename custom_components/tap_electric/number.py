from homeassistant.components.number import NumberEntity
from .const import DOMAIN

async def async_setup_entry(hass, entry, async_add_entities):
    coordinator = hass.data[DOMAIN][entry.entry_id]
    entities = []
    for charger in coordinator.data.get("chargers", []):
        entities.append(TapCurrentLimit(coordinator, charger["id"]))
    async_add_entities(entities)

class TapCurrentLimit(NumberEntity):
    def __init__(self, coordinator, charger_id):
        self.coordinator = coordinator
        self.charger_id = charger_id
        self._attr_name = "Laadstroom Limiet"
        self._attr_unique_id = f"tap_current_{charger_id}"
        self._attr_native_min_value = 6.0
        self._attr_native_max_value = 32.0
        self._attr_native_step = 0.1
        self._attr_native_unit_of_measurement = "A"
        self._attr_device_class = "current"

    @property
    def native_value(self):
        for charger in self.coordinator.data.get("chargers", []):
            if charger["id"] == self.charger_id:
                # We zoeken specifiek naar de API key 'Station-MaxCurrent'
                return float(charger.get("Station-MaxCurrent", 16.0))
        return 16.0

    async def set_native_value(self, value):
        # We sturen de float waarde direct door
        await self.coordinator.api.set_current_limit(self.charger_id, float(value))
        await self.coordinator.async_request_refresh()
