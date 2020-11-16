"""Tests for the sensor module."""
from gidgethub import GitHubException
from pytest_homeassistant_custom_component.async_mock import AsyncMock, MagicMock

from custom_components.github_custom.sensor import GitHubRepoSensor


async def test_async_update_success(hass, aioclient_mock):
    """Tests a fully successful async_update."""
    github = MagicMock()
    github.getitem = AsyncMock(
        side_effect=[
            # repos response
            {
                "forks_count": 1000,
                "name": "Home Assistant",
                "permissions": {"admin": False, "push": True, "pull": False},
                "stargazers_count": 9000,
                "open_issues_count": 5000,
            },
            # clones response
            {"count": 100, "uniques": 50},
            # views response
            {"count": 10000, "uniques": 5000},
            # commits response
            [
                {
                    "commit": {"message": "Did a thing."},
                    "sha": "e751664d95917dbdb856c382bfe2f4655e2a83c1",
                }
            ],
            # pulls response
            {
                "incomplete_results": False,
                "total_count": 345,
                "items": [
                    {"html_url": "https://github.com/homeassistant/core/pull/1347"}
                ],
            },
            # issues response
            [{"html_url": "https://github.com/homeassistant/core/issues/1"}],
            # releases response
            [{"html_url": "https://github.com/homeassistant/core/releases/v0.1.112"}],
        ]
    )
    sensor = GitHubRepoSensor(github, {"path": "homeassistant/core"})
    await sensor.async_update()

    expected = {
        "clones": 100,
        "clones_unique": 50,
        "forks": 1000,
        "latest_commit_message": "Did a thing.",
        "latest_commit_sha": "e751664d95917dbdb856c382bfe2f4655e2a83c1",
        "latest_open_issue_url": "https://github.com/homeassistant/core/issues/1",
        "latest_open_pull_request_url": "https://github.com/homeassistant/core/pull/1347",
        "latest_release_tag": "v0.1.112",
        "latest_release_url": "https://github.com/homeassistant/core/releases/v0.1.112",
        "name": "Home Assistant",
        "open_issues": 4655,
        "open_pull_requests": 345,
        "path": "homeassistant/core",
        "stargazers": 9000,
        "views": 10000,
        "views_unique": 5000,
    }
    assert expected == sensor.attrs
    assert expected == sensor.device_state_attributes
    assert sensor.available is True


async def test_async_update_failed():
    """Tests a failed async_update."""
    github = MagicMock()
    github.getitem = AsyncMock(side_effect=GitHubException)

    sensor = GitHubRepoSensor(github, {"path": "homeassistant/core"})
    await sensor.async_update()

    assert sensor.available is False
    assert {"path": "homeassistant/core"} == sensor.attrs
