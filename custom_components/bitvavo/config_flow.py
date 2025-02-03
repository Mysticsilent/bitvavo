import voluptuous as vol

from homeassistant import config_entries
from homeassistant.const import CONF_SCAN_INTERVAL
from homeassistant.helpers import config_validation as cv

from .const import DOMAIN, CONF_COINS, TOP_COINS

DEFAULT_SCAN_INTERVAL = 20

class BitvavoConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Config flow voor de Bitvavo integratie."""

    VERSION = 1

    async def async_step_user(self, user_input=None):
        """Stap waarin de gebruiker de configuratie invult."""
        errors = {}
        if user_input is not None:
            coins = user_input.get(CONF_COINS)
            if not coins:
                errors["base"] = "geen_coins"
            else:
                # Extra validatie kan hier worden toegevoegd
                return self.async_create_entry(title="Bitvavo Price Ticker", data=user_input)

        data_schema = vol.Schema({
            vol.Required(CONF_COINS): cv.multi_select(TOP_COINS),
            vol.Optional(CONF_SCAN_INTERVAL, default=DEFAULT_SCAN_INTERVAL): int,
        })

        return self.async_show_form(step_id="user", data_schema=data_schema, errors=errors)
