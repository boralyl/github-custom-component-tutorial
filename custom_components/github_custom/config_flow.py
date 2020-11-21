import logging
from typing import Any, Dict

from homeassistant import config_entries
from homeassistant.const import CONF_ACCESS_TOKEN, CONF_URL
import voluptuous as vol

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

DATA_SCHEMA = vol.Schema(
    {vol.REQUIRED(CONF_ACCESS_TOKEN): str, vol.Optional(CONF_URL): str}
)


class GithubCustomConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Github Custom config flow."""

    async def async_step_credentials(self, user_input: Dict[str, Any]):
        errors = {}
        if user_input is not None:
            pass

        return self.async_show_form(
            step_id="credentials", data_schema=DATA_SCEHMA, errors=errors
        )
