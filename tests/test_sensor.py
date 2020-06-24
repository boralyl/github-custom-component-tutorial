"""Tests for the sensor module."""
from gidgethub import GitHubException
from gidgethub.aiohttp import GitHubAPI
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from pytest_homeassistant.async_mock import AsyncMock, MagicMock, Mock

from custom_components.github_custom.const import BASE_API_URL
from custom_components.github_custom.sensor import GitHubRepoSensor, get_last_page_url


def test_get_last_page_url_link_none():
    """Test that when the link is None, we return None."""
    link = None
    assert get_last_page_url(link) is None


def test_get_last_page_url_no_last_rel():
    """Test that we return None if there is no last rel link."""
    link = 'Link: <https://api.github.com/repositories/12888993/issues?per_page=1&state=open&page=2>; rel="next"'
    assert get_last_page_url(link) is None


def test_get_last_page_url_link_has_last_ref():
    """Test we return the last url if there is a last rel link."""
    link = 'Link: <https://api.github.com/repositories/12888993/issues?per_page=1&state=open&page=2>; rel="next", <https://api.github.com/repositories/12888993/issues?per_page=1&state=open&page=1051>; rel="last"'
    expected = "https://api.github.com/repositories/12888993/issues?per_page=1&state=open&page=1051"
    assert expected == get_last_page_url(link)


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
            [{"html_url": "https://github.com/homeassistant/core/pull/1347"}],
            # issues response
            [{"html_url": "https://github.com/homeassistant/core/issues/1"}],
            # releases response
            [{"html_url": "https://github.com/homeassistant/core/releases/v0.1.112"}],
        ]
    )
    link = 'Link: <https://api.github.com/repositories/12888993/issues?per_page=1&state=open&page=2>; rel="next", <https://api.github.com/repositories/12888993/issues?per_page=1&state=open&page=100>; rel="last"'
    # This odd mock is to mock the async with in the `_get_total` method.
    github._session.get.return_value.__aenter__ = AsyncMock(
        return_value=Mock(headers={"Link": link})
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
        "open_issues": 0,
        "open_pull_requests": 100,
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


async def test__get_total_no_link_header(hass, aioclient_mock):
    """Test we return 0 when there is no Link header."""
    aioclient_mock.get(f"{BASE_API_URL}/repos/homeassistant/core")
    session = async_get_clientsession(hass)
    gh = GitHubAPI(session, "requester", oauth_token="oauth_token")
    sensor = GitHubRepoSensor(gh, {"path": "homeassistant/core"})
    actual = await sensor._get_total("/repos/homeassistant/core")
    assert 0 == actual


async def test__get_total_with_link_header(hass, aioclient_mock):
    """Test we return the total when there is a Link header with a last ref."""
    link = 'Link: <https://api.github.com/repositories/12888993/issues?per_page=1&state=open&page=2>; rel="next", <https://api.github.com/repositories/12888993/issues?per_page=1&state=open&page=1051>; rel="last"'
    aioclient_mock.get(
        f"{BASE_API_URL}/repos/homeassistant/core", headers={"Link": link}
    )
    session = async_get_clientsession(hass)
    gh = GitHubAPI(session, "requester", oauth_token="oauth_token")
    sensor = GitHubRepoSensor(gh, {"path": "homeassistant/core"})
    actual = await sensor._get_total("/repos/homeassistant/core")
    assert 1051 == actual
