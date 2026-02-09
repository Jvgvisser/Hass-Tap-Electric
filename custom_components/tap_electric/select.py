from homeassistant.components.select import SelectEntity
from .const import DOMAIN

async def async_setup_entry(hass, entry, async_add_entities):
    coordinator = hass.data[DOMAIN][entry.entry_id]
    entities = []
    for charger in coordinator.data.get("chargers", []):
        entities.append(TapPhaseSelect(coordinator, charger["id"]))
    async_add_entities(entities)

class TapPhaseSelect(SelectEntity):
    def __init__(self, coordinator, charger_id):
        self.coordinator = coordinator
        self.charger_id = charger_id
        self._attr_name = "Max Aantal Fasen"
        self._attr_unique_id = f"tap_phases_{charger_id}"
        self._attr_options = ["1", "3"]

    @property
    def current_option(self):
        for charger in self.coordinator.data.get("chargers", []):
            if charger["id"] == self.charger_id:
                # API geeft getal, we maken er een string van voor de select
                return str(charger.get("MaxAllowedPhases", "3"))
        return "3"

    async def async_select_option(self, option: str):
        # Stuur de keuze (1 of 3) naar de API
        await self.coordinator.api.set_phase_limit(self.charger_id, int(option))
        await self.coordinator.async_request_refresh()

    @property
    def device_info(self):
        return {"identifiers": {(DOMAIN, self.charger_id)}, "name": "Tap Electric Lader"}
