"""Diffs Garmin's activity list against what's already on intervals.icu, so
only genuinely new activities get downloaded (and, eventually, uploaded).

Matched on local start time (exact to the second) *and* moving duration
(approximately - see _DURATION_TOLERANCE_S/_PCT below). Start time alone
isn't a safe key: unlike `external_id` (which for this account's existing
intervals.icu activities is a filename-derived string from an earlier,
unrelated upload process, not a Garmin activity id) it's at least present on
both sides, but two unrelated activities can plausibly share a start second
(e.g. a bug re-splitting one Garmin activity into several starting at the
same instant), so duration is required to agree too before treating it as a
duplicate. The tolerance (rather than an exact match) is there because
Garmin's and intervals.icu's own recomputation of moving time from the same
FIT data can differ by a few seconds.
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Any

_DURATION_TOLERANCE_S = 60
_DURATION_TOLERANCE_PCT = 0.05


@dataclass(frozen=True)
class ActivitySignature:
    start_time: datetime
    duration_s: float | None


def _duration_matches(a: float | None, b: float | None) -> bool:
    if a is None or b is None:
        return False
    tolerance = max(_DURATION_TOLERANCE_S, _DURATION_TOLERANCE_PCT * max(a, b))
    return abs(a - b) <= tolerance


def _parse_garmin_signature(activity: dict[str, Any]) -> ActivitySignature | None:
    raw_start = activity.get("startTimeLocal")
    if not raw_start:
        return None
    start_time = datetime.strptime(raw_start, "%Y-%m-%d %H:%M:%S")
    # movingDuration excludes stopped time, so it's a more reliable "length"
    # than elapsedDuration for e.g. an indoor ride left running while paused.
    duration = activity.get("movingDuration") or activity.get("duration")
    return ActivitySignature(start_time=start_time, duration_s=duration)


def existing_signatures(
    intervals_activities: list[dict[str, Any]],
) -> list[ActivitySignature]:
    """Start time + moving duration of every activity already on intervals.icu."""
    signatures = []
    for a in intervals_activities:
        raw_start = a.get("start_date_local")
        if not raw_start:
            continue
        duration = a.get("moving_time") or a.get("elapsed_time")
        signatures.append(
            ActivitySignature(
                start_time=datetime.fromisoformat(raw_start), duration_s=duration
            )
        )
    return signatures


def find_new_activities(
    garmin_activities: list[dict[str, Any]],
    existing: list[ActivitySignature],
) -> list[dict[str, Any]]:
    """Garmin activities not already present on intervals.icu.

    An activity whose start time can't be read is kept rather than dropped -
    we can't confirm it's a duplicate, so err on the side of not silently
    losing it.
    """
    new_activities = []
    for activity in garmin_activities:
        signature = _parse_garmin_signature(activity)
        if signature is None:
            new_activities.append(activity)
            continue
        is_duplicate = any(
            signature.start_time == existing_sig.start_time
            and _duration_matches(signature.duration_s, existing_sig.duration_s)
            for existing_sig in existing
        )
        if not is_duplicate:
            new_activities.append(activity)
    return new_activities
