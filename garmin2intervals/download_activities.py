"""Manual test: download recent Garmin activities not already on intervals.icu
as FIT files into ./activities/.

Not part of the pytest suite (nothing in tests/ should hit the network) -
run directly with `uv run garmin2intervals-download-activities`.
"""

import logging
from datetime import date, timedelta
from pathlib import Path

from garmin2intervals.client import GarminClient
from garmin2intervals.config import load_settings
from garmin2intervals.intervals import IntervalsClient
from garmin2intervals.naming import build_filename, read_fit_summary, reverse_geocode
from garmin2intervals.sync import existing_start_times, find_new_activities

logging.basicConfig(level=logging.INFO)

ACTIVITIES_DIR = Path("activities")
DEFAULT_LIMIT = 10
INTERVALS_LOOKBACK_DAYS = 120


def main() -> None:
    settings = load_settings()
    client = GarminClient(
        email=settings.garmin_email,
        password=settings.garmin_password,
        tokenstore=settings.garmin_tokenstore,
    )
    client.login()

    activities = client.get_activities(limit=DEFAULT_LIMIT)
    print(f"Garmin has {len(activities)} recent activities.")

    if settings.intervals_api_key:
        intervals = IntervalsClient(settings.intervals_api_key, settings.intervals_athlete_id)
        oldest = (date.today() - timedelta(days=INTERVALS_LOOKBACK_DAYS)).isoformat()
        newest = date.today().isoformat()
        existing = existing_start_times(intervals.get_activities(oldest, newest))
        activities = find_new_activities(activities, existing)
        print(f"{len(activities)} of those aren't on intervals.icu yet.")
    else:
        print("INTERVALS_API_KEY not set - skipping the intervals.icu diff.")

    if not activities:
        return

    ACTIVITIES_DIR.mkdir(exist_ok=True)
    print(f"Downloading into {ACTIVITIES_DIR}/...")

    for activity in activities:
        activity_id = activity["activityId"]
        fit_bytes = client.download_activity_fit(activity_id)
        raw_path = ACTIVITIES_DIR / f"{activity_id}.fit"
        raw_path.write_bytes(fit_bytes)

        summary = read_fit_summary(fit_bytes)
        location = None
        if summary.start_lat is not None and summary.start_lon is not None:
            location = reverse_geocode(summary.start_lat, summary.start_lon)
        final_path = raw_path.rename(
            ACTIVITIES_DIR / build_filename(summary, location, activity_id)
        )
        print(f"- {final_path}")


if __name__ == "__main__":
    main()
