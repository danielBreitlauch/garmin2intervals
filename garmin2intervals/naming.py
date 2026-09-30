import io
import logging
import re
from dataclasses import dataclass
from datetime import datetime

import requests
from fitparse import FitFile

logger = logging.getLogger(__name__)

_SEMICIRCLE_TO_DEGREES = 180 / 2**31
_GEOCODE_ADDRESS_KEYS = ("city", "town", "village", "suburb", "municipality", "county")


@dataclass(frozen=True)
class FitSummary:
    start_time_local: datetime | None
    duration_s: float | None
    distance_m: float | None
    start_lat: float | None
    start_lon: float | None


def read_fit_summary(fit_bytes: bytes) -> FitSummary:
    """Read start time, duration, distance and start GPS from a FIT file's
    session message. Fields the file doesn't have come back as None.
    """
    fitfile = FitFile(io.BytesIO(fit_bytes))

    session = next(fitfile.get_messages("session"), None)
    if session is None:
        return FitSummary(None, None, None, None, None)
    fields = {f.name: f.value for f in session}

    start_time = fields.get("start_time")
    activity = next(fitfile.get_messages("activity"), None)
    if activity is not None and start_time is not None:
        activity_fields = {f.name: f.value for f in activity}
        timestamp = activity_fields.get("timestamp")
        local_timestamp = activity_fields.get("local_timestamp")
        if timestamp is not None and local_timestamp is not None:
            start_time += local_timestamp - timestamp

    lat = fields.get("start_position_lat")
    lon = fields.get("start_position_long")
    return FitSummary(
        start_time_local=start_time,
        duration_s=fields.get("total_elapsed_time"),
        distance_m=fields.get("total_distance"),
        start_lat=lat * _SEMICIRCLE_TO_DEGREES if lat is not None else None,
        start_lon=lon * _SEMICIRCLE_TO_DEGREES if lon is not None else None,
    )


def reverse_geocode(lat: float, lon: float) -> str | None:
    """Best-effort place name for a GPS point via OpenStreetMap Nominatim.

    Returns None on any failure (network, rate limit, no match) rather than
    raising - this only makes the filename nicer, it's never required.
    """
    try:
        resp = requests.get(
            "https://nominatim.openstreetmap.org/reverse",
            params={"lat": lat, "lon": lon, "format": "jsonv2", "zoom": 14},
            headers={"User-Agent": "garmin2intervals (personal use)"},
            timeout=10,
        )
        resp.raise_for_status()
        address = resp.json().get("address", {})
    except (requests.RequestException, ValueError) as e:
        logger.warning("Reverse geocoding failed for (%.5f, %.5f): %s", lat, lon, e)
        return None

    for key in _GEOCODE_ADDRESS_KEYS:
        if key in address:
            return address[key]
    return None


def _format_duration(seconds: float) -> str:
    total_minutes = round(seconds / 60)
    hours, minutes = divmod(total_minutes, 60)
    return f"{hours}h{minutes:02d}m" if hours else f"{minutes}m"


def _sanitize(text: str) -> str:
    return re.sub(r"[^\w-]+", "-", text).strip("-")


def build_filename(
    summary: FitSummary,
    location: str | None,
    activity_id: int | str,
    suffix: str = ".fit",
) -> str:
    """`{date}_{time}[_{location}][_{duration}]_{activity_id}{suffix}`."""
    if summary.start_time_local is not None:
        parts = [summary.start_time_local.strftime("%Y-%m-%d_%H%M")]
    else:
        parts = ["unknown-date"]
    if location:
        parts.append(_sanitize(location))
    if summary.duration_s:
        parts.append(_format_duration(summary.duration_s))
    parts.append(str(activity_id))
    return "_".join(parts) + suffix
