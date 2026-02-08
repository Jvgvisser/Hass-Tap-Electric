import aiohttp
import logging
from .const import BASE_URL

_LOGGER = logging.getLogger(__name__)

class TapElectricAPI:
    def __init__(self, api_key):
        self.api_key = api_key
        self.headers = {"X-Api-Key": self.api_key}

    async def get_chargers(self):
        """Haal alle laders op."""
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{BASE_URL}/chargers", headers=self.headers) as resp:
                return await resp.json() if resp.status == 200 else []

    async def get_active_sessions(self):
        """Haal actieve laadsessies op voor sensoren."""
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{BASE_URL}/charger-sessions", headers=self.headers) as resp:
                return await resp.json() if resp.status == 200 else []

    async def set_charging_limit(self, charger_id, amps):
        """Stel de maximale laadstroom in."""
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

    async def remote_start(self, charger_id):
        """Start de lader op afstand."""
        url = f"{BASE_URL}/chargers/{charger_id}/remote-control"
        payload = {"command": "RemoteStartTransaction"}
        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=payload, headers=self.headers) as resp:
                return resp.status == 200

    async def remote_stop(self, charger_id):
        """Stop de lader op afstand."""
        url = f"{BASE_URL}/chargers/{charger_id}/remote-control"
        payload = {"command": "RemoteStopTransaction"}
        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=payload, headers=self.headers) as resp:
                return resp.status == 200

    async def set_phases(self, charger_id, phase_count):
        """Wissel tussen 1 en 3 fasen (Geoptimaliseerd voor Alfen)."""
        url = f"{BASE_URL}/chargers/{charger_id}/remote-configuration"
        payload = {
            "command": "ChangeConfiguration",
            "args": {
                "key": "NumberOfPhases",
                "value": str(phase_count)
            }
        }
        async with aiohttp.ClientSession() as session:
            try:
                async with session.post(url, json=payload, headers=self.headers) as resp:
                    _LOGGER.info("Alfen fase-switch naar %s succesvol: %s", phase_count, resp.status == 200)
                    return resp.status == 200
            except Exception as e:
                _LOGGER.error("Fout bij aanpassen fasen op Alfen: %s", e)
                return False
