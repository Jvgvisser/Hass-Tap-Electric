from homeassistant.components.sensor import SensorEntity, SensorDeviceClass
from .const import DOMAIN
import logging

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass, entry, async_add_entities):
    coordinator = hass.data[DOMAIN][entry.entry_id]
    entities = []
    
    for charger in coordinator.data.get("chargers", []):
        charger_id = charger["id"]
        charger_name = charger.get("name") or f"Tap {charger_id[-4:]}"
        
        # 1. Maak sensoren voor elk veld in de lader-data
        for key, value in charger.items():
            if isinstance(value, (int, float, str)) and key != "id":
                entities.append(TapDynamicSensor(coordinator, charger_id, charger_name, key, "charger"))
        
        # 2. Maak sensoren voor elk veld in de actieve sessies
        sessions = coordinator.data.get("sessions", [])
        for session in sessions:
            if session.get("chargerId") == charger_id or session.get("charger", {}).get("id") == charger_id:
                for key, value in session.items():
                    if isinstance(value, (int, float, str)) and key != "id":
                        entities.append(TapDynamicSensor(coordinator, charger_id, charger_name, key, "session"))

    async_add_entities(entities)

class TapDynamicSensor(SensorEntity):
    """Een sensor die zichzelf configureert op basis van API keys."""
    def __init__(self, coordinator, charger_id, charger_name, key, source_type):
        self.coordinator = coordinator
        self.charger_id = charger_id
        self.key = key
        self.source_type = source_type
        self._attr_name = f"{charger_name} {source_type.capitalize()} {key.replace('_', ' ').capitalize()}"
        self._attr_unique_id = f"tap_{charger_id}_{source_type}_{key}"
        self._attr_has_entity_name = False

    @property
    def native_value(self):
        # Zoek de data op in de coordinator
        if self.source_type == "charger":
            for c in self.coordinator.data.get("chargers", []):
                if c["id"] == self.charger_id:
                    return c.get(self.key)
        else:
            for s in self.coordinator.data.get("sessions", []):
                if s.get("chargerId") == self.charger_id or s.get("charger", {}).get("id") == self.charger_id:
                    return s.get(self.key)
        return None

    @property
    def device_info(self):
        return {"identifiers": {(DOMAIN, self.charger_id)}, "name": self.charger_name}

    @property
    def available(self):
        return self.coordinator.last_update_success

    async def async_added_to_hass(self):
        self.async_on_remove(self.coordinator.async_add_listener(self.async_write_ha_state))
