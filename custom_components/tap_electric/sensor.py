from homeassistant.components.sensor import SensorEntity
from .const import DOMAIN
import logging

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass, entry, async_add_entities):
    coordinator = hass.data[DOMAIN][entry.entry_id]
    entities = []
    
    # We lopen door alle data in de coordinator
    # Chargers
    for charger in coordinator.data.get("chargers", []):
        c_id = charger.get("id", "unknown_charger")
        c_name = charger.get("name") or f"Tap Lader {c_id[-4:]}"
        
        for key, value in charger.items():
            if isinstance(value, (int, float, str)) and key != "id":
                entities.append(TapDynamicSensor(coordinator, c_id, c_name, key, "charger"))

    # Sessions (Live data)
    for session in coordinator.data.get("sessions", []):
        s_id = session.get("id", "unknown_session")
        # Probeer te koppelen aan charger_id voor groepering
        c_id = session.get("chargerId") or "session_data"
        
        for key, value in session.items():
            if isinstance(value, (int, float, str)) and key != "id":
                entities.append(TapDynamicSensor(coordinator, c_id, "Tap Sessie", f"sess_{key}", "session"))

    async_add_entities(entities)

class TapDynamicSensor(SensorEntity):
    def __init__(self, coordinator, charger_id, charger_name, key, source):
        self.coordinator = coordinator
        self.charger_id = charger_id
        self.charger_name = charger_name
        self.key = key
        self.source = source
        self._attr_name = f"{charger_name} {key.replace('_', ' ').capitalize()}"
        self._attr_unique_id = f"tap_{charger_id}_{source}_{key}"
        self._attr_has_entity_name = False

    @property
    def native_value(self):
        if not self.coordinator.data:
            return None
        
        if self.source == "charger":
            for c in self.coordinator.data.get("chargers", []):
                if c.get("id") == self.charger_id:
                    return c.get(self.key)
        else:
            for s in self.coordinator.data.get("sessions", []):
                if (s.get("chargerId") == self.charger_id or 
                    s.get("id") == self.key.replace("sess_","")):
                    return s.get(self.key.replace("sess_", ""))
        return None

    @property
    def device_info(self):
        # Dit was de boosdoener. Nu veilig opgezet:
        return {
            "identifiers": {(DOMAIN, self.charger_id)},
            "name": self.charger_name,
            "manufacturer": "Tap Electric",
        }

    @property
    def available(self):
        return self.coordinator.last_update_success

    async def async_added_to_hass(self):
        self.async_on_remove(self.coordinator.async_add_listener(self.async_write_ha_state))
