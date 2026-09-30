from unittest.mock import MagicMock, patch

import pytest
from garminconnect import GarminConnectAuthenticationError

from garmin2intervals.client import GarminClient


@pytest.fixture
def mock_garmin():
    with patch("garmin2intervals.client.Garmin") as mock_cls:
        yield mock_cls.return_value


def test_login_success(mock_garmin):
    mock_garmin.login.return_value = (None, None)
    client = GarminClient(email="a@b.com", password="pw", tokenstore=".tokens")

    client.login()

    mock_garmin.login.assert_called_once_with(".tokens")


def test_login_requires_mfa_without_cached_token(mock_garmin):
    mock_garmin.login.return_value = ("needs_mfa", None)
    client = GarminClient(email="a@b.com", password="pw", tokenstore=".tokens")

    with pytest.raises(GarminConnectAuthenticationError):
        client.login()


def test_get_activities_returns_list(mock_garmin):
    mock_garmin.get_activities.return_value = [{"activityName": "Run"}]
    client = GarminClient(email="a@b.com", password="pw", tokenstore=".tokens")

    activities = client.get_activities(limit=5)

    assert activities == [{"activityName": "Run"}]
    mock_garmin.get_activities.assert_called_once_with(start=0, limit=5)


def test_get_activities_handles_non_list_response(mock_garmin):
    mock_garmin.get_activities.return_value = None
    client = GarminClient(email="a@b.com", password="pw", tokenstore=".tokens")

    assert client.get_activities() == []


def test_connectapi_passthrough(mock_garmin):
    mock_garmin.connectapi.return_value = {"ok": True}
    client = GarminClient(email="a@b.com", password="pw", tokenstore=".tokens")

    result = client.connectapi("/some/path", params={"x": "1"})

    assert result == {"ok": True}
    mock_garmin.connectapi.assert_called_once_with("/some/path", params={"x": "1"})
