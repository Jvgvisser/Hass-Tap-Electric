import aiohttp
import logging
from .const import BASE_URL

_LOGGER = logging.getLogger(__name__)

class TapElectricAPI:
    def __init__(self, api_key):
        self.api_key = api_key
        self.headers = {"X-Api-Key": self.api_key}

    async def get_chargers(self):
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{BASE_URL}/chargers", headers=self.headers) as resp:
                return await resp.json()

    async def get_active_sessions(self):
        """Haal actieve laadsessies op voor Wh en kosten."""
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{BASE_URL}/charger-sessions", headers=self.headers) as resp:
                return await resp.json()

    async def set_charging_limit(self, charger_id, amps):
        """Verstuurt een OCPP SetChargingProfile commando voor de stroomsterkte."""
        url = f"{BASE_URL}/chargers/{charger_id}/remote-configuration"
        payload = {
            "command": "SetChargingProfile",
            "args": {
                "limit": float(amps),
                "unit": "A",
                "stackLevel": 1,
                "purpose": "TxProfile"
            }
        }
        async with aiohttp.ClientSession() as session:
            try:
                async with session.post(url, json=payload, headers=self.headers) as resp:
                    return resp.status == 200
            except Exception as e:
                _LOGGER.error("Fout bij instellen limiet: %s", e)
                return False

    async def set_phases(self, charger_id, phase_count):
        """
        Schakel tussen 1 en 3 fasen. 
        LET OP: Dit werkt alleen als je lader dit ondersteunt via de Tap API.
        """
        url = f"{BASE_URL}/chargers/{charger_id}/remote-configuration"
        # Voor veel laders werkt dit via een ChangeConfiguration commando
        payload = {
            "command": "ChangeConfiguration",
            "args": {
                "key": "ConnectorPhaseRotation", # Of een merk-specifieke key
                "value": "1" if phase_count == 1 else "3"
            }
        }
        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=payload, headers=self.headers) as resp:
                return resp.status == 200
