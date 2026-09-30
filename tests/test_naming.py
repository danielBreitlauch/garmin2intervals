from datetime import datetime
from pathlib import Path
from unittest.mock import patch

import requests

from garmin2intervals.naming import (
    FitSummary,
    build_filename,
    intervals_external_id,
    read_fit_summary,
    reverse_geocode,
)

FIXTURE = Path(__file__).parent / "fixtures" / "sample.fit"


def test_read_fit_summary_parses_real_file():
    summary = read_fit_summary(FIXTURE.read_bytes())

    assert summary.start_time_local == datetime(2026, 9, 20, 11, 10, 50)
    assert summary.duration_s == 1045.652
    assert summary.distance_m == 7128.18
    assert summary.start_lat == 626770921 * (180 / 2**31)
    assert summary.start_lon == 163570700 * (180 / 2**31)


def test_build_filename_includes_all_available_parts():
    summary = FitSummary(
        start_time_local=datetime(2026, 9, 20, 11, 10, 50),
        duration_s=1045.652,
        distance_m=7128.18,
        start_lat=52.6,
        start_lon=13.5,
    )

    name = build_filename(summary, "Altlandsberg", 24540409306)

    assert name == "2026-09-20_1110_Altlandsberg_17m_24540409306.fit"


def test_build_filename_omits_missing_location_and_duration():
    summary = FitSummary(
        start_time_local=datetime(2026, 9, 22, 18, 33, 23),
        duration_s=None,
        distance_m=None,
        start_lat=None,
        start_lon=None,
    )

    name = build_filename(summary, None, 24540413971)

    assert name == "2026-09-22_1833_24540413971.fit"


def test_build_filename_formats_hours():
    summary = FitSummary(
        start_time_local=datetime(2026, 9, 27, 15, 57, 20),
        duration_s=9039.268,
        distance_m=55652.46,
        start_lat=52.6,
        start_lon=13.5,
    )

    name = build_filename(summary, "Berlin", 1)

    assert name == "2026-09-27_1557_Berlin_2h31m_1.fit"


def test_intervals_external_id_matches_existing_upload_convention():
    summary = FitSummary(
        start_time_local=datetime(2026, 9, 19, 19, 29, 6),
        duration_s=None,
        distance_m=None,
        start_lat=None,
        start_lon=None,
    )

    assert intervals_external_id(summary) == "2026-09-19-19-29-06.fit"


def test_intervals_external_id_none_without_start_time():
    summary = FitSummary(None, None, None, None, None)

    assert intervals_external_id(summary) is None


def test_reverse_geocode_returns_first_matching_address_key():
    mock_response = _mock_json_response({"address": {"town": "Altlandsberg"}})

    with patch("garmin2intervals.naming.requests.get", return_value=mock_response):
        assert reverse_geocode(52.6, 13.7) == "Altlandsberg"


def test_reverse_geocode_returns_none_on_request_failure():
    with patch(
        "garmin2intervals.naming.requests.get",
        side_effect=requests.RequestException("boom"),
    ):
        assert reverse_geocode(52.6, 13.7) is None


def _mock_json_response(payload):
    class _Resp:
        def raise_for_status(self):
            pass

        def json(self):
            return payload

    return _Resp()
