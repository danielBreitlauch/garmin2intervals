from unittest.mock import MagicMock, patch

from garmin2intervals.intervals import IntervalsClient


def test_get_activities_calls_expected_url_and_auth():
    mock_resp = MagicMock()
    mock_resp.json.return_value = [{"id": "i1"}]

    with patch("garmin2intervals.intervals.requests.get", return_value=mock_resp) as get:
        client = IntervalsClient(api_key="secret", athlete_id="i42")
        result = client.get_activities("2026-01-01", "2026-01-31")

    assert result == [{"id": "i1"}]
    get.assert_called_once_with(
        "https://intervals.icu/api/v1/athlete/i42/activities",
        params={"oldest": "2026-01-01", "newest": "2026-01-31"},
        auth=("API_KEY", "secret"),
        timeout=30,
    )
    mock_resp.raise_for_status.assert_called_once()


def test_get_activities_defaults_to_athlete_alias_zero():
    mock_resp = MagicMock()
    mock_resp.json.return_value = []

    with patch("garmin2intervals.intervals.requests.get", return_value=mock_resp) as get:
        IntervalsClient(api_key="secret").get_activities("2026-01-01", "2026-01-31")

    assert get.call_args.args[0] == "https://intervals.icu/api/v1/athlete/0/activities"
