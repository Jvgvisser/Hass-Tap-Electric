import aiohttp
import logging

_LOGGER = logging.getLogger(__name__)

class TapElectricAPI:
    def __init__(self, token):
        self.token = token
        self.base_url = "https://api.tapelectric.app/v1"
        # De headers moeten exact zijn voor de Tap API om 401 te voorkomen
        self.headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json",
            "Accept": "application/json"
        }

    async def get_data(self):
        """Haal alle chargers en actieve sessies op in één verzoek."""
        async with aiohttp.ClientSession() as session:
            try:
                # 1. Haal laders op
                async with session.get(f"{self.base_url}/chargers", headers=self.headers) as resp:
                    if resp.status == 401:
                        _LOGGER.error("Tap API 401: Onbevoegd. Controleer of je API-key correct is.")
                        return {"chargers": [], "sessions": []}
                    
                    if resp.status != 200:
                        text = await resp.text()
                        _LOGGER.error("Tap API Fout bij chargers: Status %s - %s", resp.status, text)
                        chargers = []
                    else:
                        chargers = await resp.json()
                
                # 2. Haal actieve sessies op
                async with session.get(f"{self.base_url}/sessions", headers=self.headers) as resp:
                    if resp.status == 200:
                        sessions = await resp.json()
                    else:
                        sessions = []

                return {
                    "chargers": chargers,
                    "sessions": sessions
                }
            except Exception as e:
                _LOGGER.error("Kritieke fout bij ophalen Tap data: %s", e)
                return {"chargers": [], "sessions": []}

    async def remote_start(self, charger_id, connector_id=1):
        """Start een laadsessie op afstand."""
        url = f"{self.base_url}/chargers/{charger_id}/remote-start"
        async with aiohttp.ClientSession() as session:
            payload = {"connectorId": connector_id}
            async with session.post(url, headers=self.headers, json=payload) as resp:
                _LOGGER.debug("Remote start status: %s", resp.status)
                return resp.status in [200, 201]

    async def remote_stop(self, charger_id):
        """Stop/Pauzeer de laadsessie op afstand."""
        url = f"{self.base_url}/chargers/{charger_id}/remote-stop"
        async with aiohttp.ClientSession() as session:
            # Sommige API's vereisen een lege JSON body {} bij een POST
            async with session.post(url, headers=self.headers, json={}) as resp:
                _LOGGER.debug("Remote stop status: %s", resp.status)
                return resp.status in [200, 201]

    async def set_current_limit(self, charger_id, amps):
        """Stel de Station-MaxCurrent in (werkt met floats)."""
        url = f"{self.base_url}/chargers/{charger_id}/settings"
        async with aiohttp.ClientSession() as session:
            payload = {"Station-MaxCurrent": float(amps)}
            async with session.patch(url, headers=self.headers, json=payload) as resp:
                _LOGGER.debug("Set current limit status: %s", resp.status)
                return resp.status == 200

    async def set_phase_limit(self, charger_id, phases):
        """Stel MaxAllowedPhases in (meestal 1 of 3)."""
        url = f"{self.base_url}/chargers/{charger_id}/settings"
        async with aiohttp.ClientSession() as session:
            payload = {"MaxAllowedPhases": int(phases)}
            async with session.patch(url, headers=self.headers, json=payload) as resp:
                _LOGGER.debug("Set phase limit status: %s", resp.status)
                return resp.status == 200
