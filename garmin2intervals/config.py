"""Environment-variable configuration, loaded from .env via python-dotenv."""

import os
from dataclasses import dataclass

from dotenv import load_dotenv

load_dotenv()


@dataclass(frozen=True)
class Settings:
    garmin_email: str
    garmin_password: str
    garmin_tokenstore: str
    intervals_api_key: str | None
    intervals_athlete_id: str


def load_settings() -> Settings:
    email = os.environ["GARMIN_EMAIL"]
    password = os.environ["GARMIN_PASSWORD"]
    tokenstore = os.getenv("GARMINTOKENS", ".garmin_tokens")
    return Settings(
        garmin_email=email,
        garmin_password=password,
        garmin_tokenstore=tokenstore,
        intervals_api_key=os.getenv("INTERVALS_API_KEY"),
        # "0" is intervals.icu's alias for "the athlete owning the API key" -
        # no need to know your own numeric athlete id.
        intervals_athlete_id=os.getenv("INTERVALS_ATHLETE_ID", "0"),
    )
