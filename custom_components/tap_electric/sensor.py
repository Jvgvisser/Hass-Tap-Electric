from homeassistant.components.sensor import SensorEntity, SensorDeviceClass, SensorStateClass
from homeassistant.const import UnitOfEnergy, UnitOfElectricCurrent, UnitOfElectricPotential, UnitOfPower
from .const import DOMAIN
import logging

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass, entry, async_add_entities):
    coordinator = hass.data[DOMAIN][entry.entry_id]
    entities = []
    
    for charger in coordinator.data.get("chargers", []):
        charger_id = charger["id"]
        # Forceer de gewenste naam
        full_name = charger.get("name")
        if not full_name or "e-42" in full_name:
            full_name = "Bartoutszate-42"
            
        entities.append(TapStatusSensor(coordinator, charger_id, full_name))
        entities.append(TapEnergySensor(coordinator, charger_id, full_name))
        entities.append(TapPowerSensor(coordinator, charger_id, full_name))
        entities.append(TapVoltageSensor(coordinator, charger_id, full_name))
        entities.append(TapCurrentSensor(coordinator, charger_id, full_name))
        
    async_add_entities(entities)

class TapBaseSensor(SensorEntity):
    def __init__(self, coordinator, charger_id, full_name):
        self.coordinator = coordinator
        self.charger_id = charger_id
        self.full_name = full_name
        self._attr_has_entity_name = False
        
    @property
    def device_info(self):
        return {
            "identifiers": {(DOMAIN, self.charger_id)},
            "name": self.full_name,
            "manufacturer": "Alfen (via Tap)",
        }

    @property
    def available(self):
        return self.coordinator.last_update_success

    async def async_added_to_hass(self):
        self.async_on_remove(self.coordinator.async_add_listener(self.async_write_ha_state))

class TapPowerSensor(TapBaseSensor):
    _attr_device_class = SensorDeviceClass.POWER
    _attr_native_unit_of_measurement = UnitOfPower.WATT
    _attr_state_class = SensorStateClass.MEASUREMENT

    @property
    def name(self): return f"{self.full_name} Vermogen"
    @property
    def unique_id(self): return f"tap_power_{self.charger_id}"

    @property
    def native_value(self):
        # 1. Check actieve sessies
        sessions = self.coordinator.data.get("sessions", [])
        for s in sessions:
            # Check beide mogelijke ID velden
            s_id = s.get("chargerId") or s.get("charger_id")
            if s_id == self.charger_id:
                # Check verschillende mogelijke veldnamen voor Wattage
                return s.get("activeImport") or s.get("active_import") or s.get("power", 0)
        
        # 2. Check charger data zelf (sommige API versies zetten het hier)
        for c in self.coordinator.data.get("chargers", []):
            if c["id"] == self.charger_id:
                return c.get("lastKnownPower") or c.get("activeImport", 0)
        return 0

class TapCurrentSensor(TapBaseSensor):
    _attr_device_class = SensorDeviceClass.CURRENT
    _attr_native_unit_of_measurement = UnitOfElectricCurrent.AMPERE

    @property
    def name(self): return f"{self.full_name} Stroomsterkte"
    @property
    def unique_id(self): return f"tap_current_{self.charger_id}"

    @property
    def native_value(self):
        sessions = self.coordinator.data.get("sessions", [])
        for s in sessions:
            s_id = s.get("chargerId") or s.get("charger_id")
            if s_id == self.charger_id:
                return s.get("currentImport") or s.get("current_import") or 0
        return 0

class TapStatusSensor(TapBaseSensor):
    @property
    def name(self): return f"{self.full_name} Status"
    @property
    def unique_id(self): return f"tap_status_{self.charger_id}"
    @property
    def state(self):
        for c in self.coordinator.data.get("chargers", []):
            if c["id"] == self.charger_id:
                return c.get("status", "Unknown")
        return "Unknown"

class TapEnergySensor(TapBaseSensor):
    _attr_device_class = SensorDeviceClass.ENERGY
    _attr_native_unit_of_measurement = "kWh"
    _attr_state_class = SensorStateClass.TOTAL_INCREASING

    @property
    def name(self): return f"{self.full_name} Totaal Energie"
    @property
    def unique_id(self): return f"tap_total_energy_{self.charger_id}"

    @property
    def native_value(self):
        for c in self.coordinator.data.get("chargers", []):
            if c["id"] == self.charger_id:
                # Alfen geeft vaak Wh, we rekenen om naar kWh
                wh = c.get("totalWh") or c.get("total_wh") or 0
                return round(wh / 1000, 2)
        return 0

class TapVoltageSensor(TapBaseSensor):
    _attr_device_class = SensorDeviceClass.VOLTAGE
    _attr_native_unit_of_measurement = UnitOfElectricPotential.VOLT

    @property
    def name(self): return f"{self.full_name} Voltage"
    @property
    def unique_id(self): return f"tap_voltage_{self.charger_id}"

    @property
    def native_value(self):
        sessions = self.coordinator.data.get("sessions", [])
        for s in sessions:
            s_id = s.get("chargerId") or s.get("charger_id")
            if s_id == self.charger_id:
                return s.get("voltage") or s.get("average_voltage") or 230
        return 230
