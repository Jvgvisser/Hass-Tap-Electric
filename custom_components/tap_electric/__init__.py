async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    api = TapElectricAPI(entry.data["api_key"])
    # Sla de API los op zodat de slider erbij kan
    hass.data.setdefault(DOMAIN, {})["api_instance"] = api
    
    async def async_update_data():
        chargers = await api.get_chargers()
        sessions = await api.get_active_sessions()
        return {"chargers": chargers, "sessions": sessions}

    coordinator = DataUpdateCoordinator(
        hass,
        _LOGGER,
        name="Tap Electric",
        update_method=async_update_data,
        update_interval=timedelta(seconds=30),
    )

    await coordinator.async_config_entry_first_refresh()
    hass.data[DOMAIN][entry.entry_id] = coordinator

    await hass.config_entries.async_forward_entry_setups(entry, ["sensor", "number"])
    return True
