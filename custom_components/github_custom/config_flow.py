import logging
from typing import Any, Dict, Optional

from gidgethub import BadRequest
from gidgethub.aiohttp import GitHubAPI
from homeassistant import config_entries
from homeassistant.const import CONF_ACCESS_TOKEN, CONF_NAME, CONF_PATH, CONF_URL
from homeassistant.helpers.aiohttp_client import async_get_clientsession
import homeassistant.helpers.config_validation as cv
import voluptuous as vol

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

AUTH_SCHEMA = vol.Schema(
    {vol.Required(CONF_ACCESS_TOKEN): cv.string, vol.Optional(CONF_URL): cv.string}
)
REPO_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_PATH): cv.string,
        vol.Optional(CONF_NAME): cv.string,
        vol.Optional("add_another"): cv.boolean,
    }
)


def validate_path(path: str) -> None:
    """Validates a GitHub repo path.

    Raises a ValueError if the path is invalid.
    """
    if len(path.split("/")) != 2:
        raise ValueError


class GithubCustomConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Github Custom config flow."""

    async def async_step_user(self, user_input: Optional[Dict[str, Any]] = None):
        """Invoked when a user initiates a flow via the user interface."""
        errors: Dict[str, str] = {}
        if user_input is not None:
            # Validate that the auth token is valid.
            session = async_get_clientsession(self.hass)
            gh = GitHubAPI(
                session, "requester", oauth_token=user_input[CONF_ACCESS_TOKEN]
            )
            try:
                await gh.getitem("repos/home-assistant/core")
            except BadRequest:
                # Invalid set `auth` error.
                errors["base"] = "auth"
            if not errors:
                # Input is valid, set data.
                self.data = user_input
                self.data["repos"] = []
                # Return the form of the next step.
                return await self.async_step_repo()

        return self.async_show_form(
            step_id="user", data_schema=AUTH_SCHEMA, errors=errors
        )

    async def async_step_repo(self, user_input: Optional[Dict[str, Any]] = None):
        """Second step in config flow to add a repo to watch."""
        errors: Dict[str, str] = {}
        if user_input is not None:
            try:
                validate_path(user_input[CONF_PATH])
            except ValueError:
                errors["base"] = "invalid_path"

            if not errors:
                self.data["repos"].append(
                    {
                        "path": user_input[CONF_PATH],
                        "name": user_input.get(CONF_NAME, user_input[CONF_PATH]),
                    }
                )
                if user_input.get("add_another", False):
                    return await self.async_step_repo()

                _LOGGER.warning("user_input: %s - %s", user_input, self.data)

        return self.async_show_form(
            step_id="repo", data_schema=REPO_SCHEMA, errors=errors
        )
