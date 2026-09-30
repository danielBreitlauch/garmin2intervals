"""Diffs Garmin's activity list against what's already on intervals.icu, so
only genuinely new activities get downloaded (and, eventually, uploaded).

Matched by local start time, exact to the second: intervals.icu's
`start_date_local` and Garmin's `startTimeLocal` both describe the same
wall-clock moment a recording started, which is a reliable identity across
the two systems - unlike `external_id`, which for this account's existing
intervals.icu activities is a filename-derived string from an earlier,
unrelated upload process, not a Garmin activity id.
"""

from datetime import datetime
from typing import Any


def _parse_garmin_local_start(activity: dict[str, Any]) -> datetime | None:
    raw = activity.get("startTimeLocal")
    if not raw:
        return None
    return datetime.strptime(raw, "%Y-%m-%d %H:%M:%S")


def existing_start_times(intervals_activities: list[dict[str, Any]]) -> set[datetime]:
    """Local start timestamps already on intervals.icu."""
    return {
        datetime.fromisoformat(a["start_date_local"])
        for a in intervals_activities
        if a.get("start_date_local")
    }


def find_new_activities(
    garmin_activities: list[dict[str, Any]],
    existing: set[datetime],
) -> list[dict[str, Any]]:
    """Garmin activities not already present on intervals.icu.

    An activity whose start time can't be read is kept rather than dropped -
    we can't confirm it's a duplicate, so err on the side of not silently
    losing it.
    """
    new_activities = []
    for activity in garmin_activities:
        start = _parse_garmin_local_start(activity)
        if start is None or start not in existing:
            new_activities.append(activity)
    return new_activities
