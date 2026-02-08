from homeassistant.components.sensor import SensorEntity, SensorDeviceClass, SensorStateClass
from homeassistant.const import UnitOfEnergy, UnitOfElectricCurrent, UnitOfElectricPotential, UnitOfPower
from .const import DOMAIN

async def async_setup_entry(hass, entry, async_add_entities):
    coordinator = hass.data[DOMAIN][entry.entry_id]
    entities = []

    for charger in coordinator.data.get("chargers", []):
        charger_id = charger["id"]
        charger_name = charger.get("name", f"Lader {charger_id[-4:]}")
        
        # Basis sensoren
        entities.append(TapStatusSensor(coordinator, charger_id, charger_name))
        entities.append(TapEnergySensor(coordinator, charger_id, charger_name))
        entities.append(TapCostSensor(coordinator, charger_id, charger_name))
        
        # Power & Voltage sensoren
        entities.append(TapPowerSensor(coordinator, charger_id, charger_name))
        entities.append(TapVoltageSensor(coordinator, charger_id, charger_name))
        entities.append(TapCurrentSensor(coordinator, charger_id, charger_name))
        
    async_add_entities(entities)

class TapBaseSensor(SensorEntity):
    def __init__(self, coordinator, charger_id, charger_name):
        self.coordinator = coordinator
        self.charger_id = charger_id
        self.charger_name = charger_name
        
    @property
    def device_info(self):
        return {
            "identifiers": {(DOMAIN, self.charger_id)},
            "name": self.charger_name,
            "manufacturer": "Tap Electric",
        }

    @property
    def should_poll(self): return False
    @property
    def available(self): return self.coordinator.last_update_success

    async def async_added_to_hass(self):
        self.async_on_remove(self.coordinator.async_add_listener(self.async_write_ha_state))

class TapStatusSensor(TapBaseSensor):
    @property
    def name(self): return f"{self.charger_name} Status"
    @property
    def unique_id(self): return f"tap_status_{self.charger_id}"
    @property
    def state(self):
        for c in self.coordinator.data.get("chargers", []):
            if c["id"] == self.charger_id: return c.get("status")
        return "Unknown"

class TapPowerSensor(TapBaseSensor):
    """Actueel vermogen in Watt."""
    _attr_device_class = SensorDeviceClass.POWER
    _attr_native_unit_of_measurement = UnitOfPower.WATT
    _attr_state_class = SensorStateClass.MEASUREMENT
    @property
    def name(self): return f"{self.charger_name} Vermogen"
    @property
    def unique_id(self): return f"tap_power_{self.charger_id}"
    @property
    def native_value(self):
        for s in self.coordinator.data.get("sessions", []):
            if s.get("chargerId") == self.charger_id: return s.get("activeImport")
        return 0

class TapVoltageSensor(TapBaseSensor):
    """Voltage op de lader."""
    _attr_device_class = SensorDeviceClass.VOLTAGE
    _attr_native_unit_of_measurement = UnitOfElectricPotential.VOLT
    @property
    def name(self): return f"{self.charger_name} Voltage"
    @property
    def unique_id(self): return f"tap_voltage_{self.charger_id}"
    @property
    def native_value(self):
        for s in self.coordinator.data.get("sessions", []):
            if s.get("chargerId") == self.charger_id: return s.get("voltage")
        return 0

class TapCurrentSensor(TapBaseSensor):
    """Actuele stroomsterkte in Ampère."""
    _attr_device_class = SensorDeviceClass.CURRENT
    _attr_native_unit_of_measurement = UnitOfElectricCurrent.AMPERE
    @property
    def name(self): return f"{self.charger_name} Stroomsterkte"
    @property
    def unique_id(self): return f"tap_current_{self.charger_id}"
    @property
    def native_value(self):
        for s in self.coordinator.data.get("sessions", []):
            if s.get("chargerId") == self.charger_id: return s.get("currentImport")
        return 0

class TapEnergySensor(TapBaseSensor):
    _attr_device_class = SensorDeviceClass.ENERGY
    _attr_native_unit_of_measurement = UnitOfEnergy.WATT_HOUR
    _attr_state_class = SensorStateClass.TOTAL_INCREASING
    @property
    def name(self): return f"{self.charger_name} Energie"
    @property
    def unique_id(self): return f"tap_energy_{self.charger_id}"
    @property
    def native_value(self):
        for s in self.coordinator.data.get("sessions", []):
            if s.get("chargerId") == self.charger_id: return s.get("wh")
        return 0

class TapCostSensor(TapBaseSensor):
    _attr_device_class = SensorDeviceClass.MONETARY
    _attr_native_unit_of_measurement = "EUR"
    @property
    def name(self): return f"{self.charger_name} Kosten"
    @property
    def unique_id(self): return f"tap_cost_{self.charger_id}"
    @property
    def native_value(self):
        for s in self.coordinator.data.get("sessions", []):
            if s.get("chargerId") == self.charger_id: return s.get("amountInclVat")
        return 0
