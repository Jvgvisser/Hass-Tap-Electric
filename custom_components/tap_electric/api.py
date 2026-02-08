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
                return await resp.json() if resp.status == 200 else []

    async def get_active_sessions(self):
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{BASE_URL}/charger-sessions", headers=self.headers) as resp:
                return await resp.json() if resp.status == 200 else []

    async def set_charging_limit(self, charger_id, amps):
        url = f"{BASE_URL}/chargers/{charger_id}/remote-configuration"
        payload = {
            "command": "SetChargingProfile",
            "args": {"limit": float(amps), "unit": "A", "stackLevel": 1, "purpose": "TxProfile"}
        }
        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=payload, headers=self.headers) as resp:
                return resp.status == 200
