"""Manual test: download recent activities as FIT files into ./activities/.

Not part of the pytest suite (nothing in tests/ should hit the network) -
run directly with `uv run garmin2intervals-download-activities`.
"""

import logging
from pathlib import Path

from garmin2intervals.client import GarminClient
from garmin2intervals.config import load_settings
from garmin2intervals.naming import build_filename, read_fit_summary, reverse_geocode

logging.basicConfig(level=logging.INFO)

ACTIVITIES_DIR = Path("activities")
DEFAULT_LIMIT = 10


def main() -> None:
    settings = load_settings()
    client = GarminClient(
        email=settings.garmin_email,
        password=settings.garmin_password,
        tokenstore=settings.garmin_tokenstore,
    )
    client.login()

    ACTIVITIES_DIR.mkdir(exist_ok=True)

    activities = client.get_activities(limit=DEFAULT_LIMIT)
    print(f"Downloading {len(activities)} activities into {ACTIVITIES_DIR}/...")

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
