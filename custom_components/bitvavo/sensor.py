import logging
import datetime
import async_timeout

from homeassistant.components.sensor import SensorEntity
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, CoordinatorEntity
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.const import CONF_SCAN_INTERVAL

from .const import DOMAIN, CONF_COINS

_LOGGER = logging.getLogger(__name__)

BASE_URL = "https://api.bitvavo.com/v2/ticker/price"

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities):
    """Setup de sensor-entiteiten via de config entry."""
    config = entry.data
    coins = config.get(CONF_COINS)
    if not coins:
        _LOGGER.error("Geen coins geconfigureerd voor Bitvavo")
        return

    scan_interval_seconds = config.get(CONF_SCAN_INTERVAL, 20)
    scan_interval = datetime.timedelta(seconds=int(scan_interval_seconds))

    session = async_get_clientsession(hass)

    async def async_update_data():
        """Haal data op van de Bitvavo API."""
        try:
            async with async_timeout.timeout(10):
                async with session.get(BASE_URL) as response:
                    if response.status != 200:
                        _LOGGER.error("Fout bij ophalen van data: %s", response.status)
                        return None
                    data = await response.json()
                    return data
        except Exception as e:
            _LOGGER.error("Exception bij ophalen van data: %s", e)
            return None

    coordinator = DataUpdateCoordinator(
        hass,
        _LOGGER,
        name="Bitvavo Price Ticker",
        update_method=async_update_data,
        update_interval=scan_interval,
    )

    await coordinator.async_config_entry_first_refresh()

    entities = []
    for coin in coins:
        entities.append(BitvavoSensor(coordinator, coin, entry))
    async_add_entities(entities, True)

class BitvavoSensor(CoordinatorEntity, SensorEntity):
    """Sensor die de prijs toont voor een specifieke crypto coin via Bitvavo."""

    def __init__(self, coordinator: DataUpdateCoordinator, coin: str, config_entry: ConfigEntry):
        """Initialiseer de sensor."""
        super().__init__(coordinator)
        self._coin = coin
        self._config_entry = config_entry
        self._name = f"Bitvavo {coin} Price"
        self._unique_id = f"{config_entry.entry_id}_{coin.lower()}"

    @property
    def name(self):
        """Retourneer de naam van de sensor."""
        return self._name

    @property
    def unique_id(self):
        """Retourneer een unieke ID voor deze sensor."""
        return self._unique_id

    @property
    def state(self):
        """Retourneer de huidige prijs voor de coin."""
        data = self.coordinator.data
        if not data:
            return None
        # De data is een lijst met dictionaries met sleutels 'market' en 'price'
        for item in data:
            if item.get("market") == self._coin:
                return item.get("price")
        return None

    @property
    def unit_of_measurement(self):
        """Bepaal de unit of measurement (bijvoorbeeld EUR)."""
        if "-" in self._coin:
            return self._coin.split("-")[1]
        return None

    @property
    def device_info(self):
        """Koppel de sensor aan een device in het apparaatregister."""
        return {
            "identifiers": {(DOMAIN, self._config_entry.entry_id)},
            "name": "Bitvavo Price Ticker",
            "manufacturer": "Bitvavo",
            "model": "Crypto Price Ticker"
        }

    @property
    def extra_state_attributes(self):
        """Retourneer extra attributen voor de sensor."""
        return {
            "coin": self._coin,
            "last_update_success": self.coordinator.last_update_success,
        }
