import logging

from garminconnect import GarminConnectAuthenticationError

from garmin2intervals.client import GarminClient
from garmin2intervals.config import load_settings

logging.basicConfig(level=logging.INFO)


def main() -> None:
    settings = load_settings()
    client = GarminClient(
        email=settings.garmin_email,
        password=settings.garmin_password,
        tokenstore=settings.garmin_tokenstore,
    )

    try:
        client.login()
    except GarminConnectAuthenticationError as e:
        print(f"Login failed: {e}")
        raise SystemExit(1) from e

    print("Login OK. Fetching 5 most recent activities...")
    for activity in client.get_activities(limit=5):
        print(f"- {activity.get('activityName')} ({activity.get('startTimeLocal')})")


if __name__ == "__main__":
    main()
