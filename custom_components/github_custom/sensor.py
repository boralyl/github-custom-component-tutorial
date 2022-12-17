"""GitHub sensor platform."""
from __future__ import annotations

from collections.abc import Callable
from datetime import timedelta
import logging
from typing import Any

from aiohttp import ClientError
import gidgethub
from gidgethub.aiohttp import GitHubAPI
from homeassistant import config_entries, core
from homeassistant.components.sensor import PLATFORM_SCHEMA
from homeassistant.const import (
    ATTR_NAME,
    CONF_ACCESS_TOKEN,
    CONF_NAME,
    CONF_PATH,
    CONF_URL,
)
from homeassistant.helpers.aiohttp_client import async_get_clientsession
import homeassistant.helpers.config_validation as cv
from homeassistant.helpers.entity import Entity
from homeassistant.helpers.typing import (
    ConfigType,
    DiscoveryInfoType,
    HomeAssistantType,
)
import voluptuous as vol

from .const import (
    ATTR_CLONES,
    ATTR_CLONES_UNIQUE,
    ATTR_FORKS,
    ATTR_LATEST_COMMIT_MESSAGE,
    ATTR_LATEST_COMMIT_SHA,
    ATTR_LATEST_OPEN_ISSUE_URL,
    ATTR_LATEST_OPEN_PULL_REQUEST_URL,
    ATTR_LATEST_RELEASE_TAG,
    ATTR_LATEST_RELEASE_URL,
    ATTR_OPEN_ISSUES,
    ATTR_OPEN_PULL_REQUESTS,
    ATTR_PATH,
    ATTR_STARGAZERS,
    ATTR_VIEWS,
    ATTR_VIEWS_UNIQUE,
    CONF_REPOS,
    DOMAIN,
)

_LOGGER = logging.getLogger(__name__)
# Time between updating data from GitHub
SCAN_INTERVAL = timedelta(minutes=10)

REPO_SCHEMA = vol.Schema(
    {vol.Required(CONF_PATH): cv.string, vol.Optional(CONF_NAME): cv.string}
)

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend(
    {
        vol.Required(CONF_ACCESS_TOKEN): cv.string,
        vol.Required(CONF_REPOS): vol.All(cv.ensure_list, [REPO_SCHEMA]),
        vol.Optional(CONF_URL): cv.url,
    }
)


async def async_setup_entry(
    hass: core.HomeAssistant,
    config_entry: config_entries.ConfigEntry,
    async_add_entities,
) -> None:
    """Setup sensors from a config entry created in the integrations UI."""
    config = hass.data[DOMAIN][config_entry.entry_id]
    # Update our config to include new repos and remove those that have been removed.
    if config_entry.options:
        config.update(config_entry.options)
    session = async_get_clientsession(hass)
    github = GitHubAPI(session, "requester", oauth_token=config[CONF_ACCESS_TOKEN])
    sensors = [GitHubRepoSensor(github, repo) for repo in config[CONF_REPOS]]
    async_add_entities(sensors, update_before_add=True)


async def async_setup_platform(
    hass: HomeAssistantType,
    config: ConfigType,
    async_add_entities: Callable,
    discovery_info: DiscoveryInfoType | None = None,
) -> None:
    """Set up the sensor platform."""
    session = async_get_clientsession(hass)
    github = GitHubAPI(session, "requester", oauth_token=config[CONF_ACCESS_TOKEN])
    sensors = [GitHubRepoSensor(github, repo) for repo in config[CONF_REPOS]]
    async_add_entities(sensors, update_before_add=True)


class GitHubRepoSensor(Entity):
    """Representation of a GitHub Repo sensor."""

    def __init__(self, github: GitHubAPI, repo: dict[str, str]):
        super().__init__()
        self.github = github
        self.repo = repo["path"]
        self.attrs: dict[str, Any] = {ATTR_PATH: self.repo}
        self._name = repo.get("name", self.repo)
        self._state = None
        self._available = True

    @property
    def name(self) -> str:
        """Return the name of the entity."""
        return self._name

    @property
    def unique_id(self) -> str:
        """Return the unique ID of the sensor."""
        return self.repo

    @property
    def available(self) -> bool:
        """Return True if entity is available."""
        return self._available

    @property
    def state(self) -> str | None:
        return self._state

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        return self.attrs

    async def async_update(self) -> None:
        """Update all sensors."""
        try:
            repo_url = f"/repos/{self.repo}"
            repo_data = await self.github.getitem(repo_url)
            self.attrs[ATTR_FORKS] = repo_data["forks_count"]
            self.attrs[ATTR_NAME] = repo_data["name"]
            self.attrs[ATTR_STARGAZERS] = repo_data["stargazers_count"]

            if repo_data["permissions"]["push"]:
                clones_url = f"{repo_url}/traffic/clones"
                clones_data = await self.github.getitem(clones_url)
                self.attrs[ATTR_CLONES] = clones_data["count"]
                self.attrs[ATTR_CLONES_UNIQUE] = clones_data["uniques"]

                views_url = f"{repo_url}/traffic/views"
                views_data = await self.github.getitem(views_url)
                self.attrs[ATTR_VIEWS] = views_data["count"]
                self.attrs[ATTR_VIEWS_UNIQUE] = views_data["uniques"]

            commits_url = f"/repos/{self.repo}/commits"
            commits_data = await self.github.getitem(commits_url)
            latest_commit = commits_data[0]
            self.attrs[ATTR_LATEST_COMMIT_MESSAGE] = latest_commit["commit"]["message"]
            self.attrs[ATTR_LATEST_COMMIT_SHA] = latest_commit["sha"]

            # Using the search api to fetch open PRs.
            prs_url = f"/search/issues?q=repo:{self.repo}+state:open+is:pr"
            prs_data = await self.github.getitem(prs_url)
            self.attrs[ATTR_OPEN_PULL_REQUESTS] = prs_data["total_count"]
            if prs_data and prs_data["items"]:
                self.attrs[ATTR_LATEST_OPEN_PULL_REQUEST_URL] = prs_data["items"][0][
                    "html_url"
                ]

            issues_url = f"/repos/{self.repo}/issues"
            issues_data = await self.github.getitem(issues_url)
            # GitHub issues include pull requests, so to just get the number of issues,
            # we need to subtract the total number of pull requests from this total.
            total_issues = repo_data["open_issues_count"]
            self.attrs[ATTR_OPEN_ISSUES] = (
                total_issues - self.attrs[ATTR_OPEN_PULL_REQUESTS]
            )
            if issues_data:
                self.attrs[ATTR_LATEST_OPEN_ISSUE_URL] = issues_data[0]["html_url"]

            releases_url = f"/repos/{self.repo}/releases"
            releases_data = await self.github.getitem(releases_url)
            if releases_data:
                self.attrs[ATTR_LATEST_RELEASE_URL] = releases_data[0]["html_url"]
                self.attrs[ATTR_LATEST_RELEASE_TAG] = releases_data[0][
                    "html_url"
                ].split("/")[-1]

            # Set state to short commit sha.
            self._state = latest_commit["sha"][:7]
            self._available = True
        except (ClientError, gidgethub.GitHubException):
            self._available = False
            _LOGGER.exception(
                "Error retrieving data from GitHub for sensor %s", self.name
            )
