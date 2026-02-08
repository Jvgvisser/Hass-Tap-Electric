from homeassistant.components.sensor import SensorEntity, SensorDeviceClass, SensorStateClass
from homeassistant.const import UnitOfEnergy, UnitOfElectricCurrent
from .const import DOMAIN

async def async_setup_entry(hass, entry, async_add_entities):
    api = hass.data[DOMAIN][entry.entry_id]
    chargers = await api.get_chargers()
    sessions = await api.get_active_sessions()
    
    entities = []
    for charger in chargers:
        # Basis Status
        entities.append(TapStatusSensor(api, charger))
        # Identificatie
        entities.append(TapDiagnosticSensor(api, charger, "Model", "model"))
        
        # Zoek of er een actieve sessie is voor deze lader
        for session in sessions:
            if session.get("chargerId") == charger["id"]:
                entities.append(TapSessionEnergySensor(api, session))
                entities.append(TapSessionCostSensor(api, session))
                
    async_add_entities(entities)

class TapStatusSensor(SensorEntity):
    def __init__(self, api, charger):
        self._charger = charger
        self._attr_name = f"Tap Electric {charger['name']} Status"
        self._attr_unique_id = f"tap_status_{charger['id']}"

    @property
    def state(self):
        return self._charger.get('status')

class TapSessionEnergySensor(SensorEntity):
    """Sensor voor verbruikte energie in de huidige sessie."""
    def __init__(self, api, session):
        self._attr_name = f"Tap Sessie Energie {session['id'][-4:]}"
        self._attr_native_unit_of_measurement = UnitOfEnergy.WATT_HOUR
        self._attr_device_class = SensorDeviceClass.ENERGY
        self._attr_state_class = SensorStateClass.TOTAL_INCREASING
        self._session = session

    @property
    def native_value(self):
        return self._session.get('wh')

class TapSessionCostSensor(SensorEntity):
    """Sensor voor de kosten van de huidige sessie."""
    def __init__(self, api, session):
        self._attr_name = f"Tap Sessie Kosten {session['id'][-4:]}"
        self._attr_native_unit_of_measurement = "EUR"
        self._attr_device_class = SensorDeviceClass.MONETARY
        self._session = session

    @property
    def native_value(self):
        return self._session.get('amountInclVat')

class TapDiagnosticSensor(SensorEntity):
    def __init__(self, api, charger, label, key):
        self._attr_name = f"Tap {charger['name']} {label}"
        self._charger = charger
        self._key = key

    @property
    def state(self):
        return self._charger.get(self._key)
