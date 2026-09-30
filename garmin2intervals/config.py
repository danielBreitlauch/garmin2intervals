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


def load_settings() -> Settings:
    email = os.environ["GARMIN_EMAIL"]
    password = os.environ["GARMIN_PASSWORD"]
    tokenstore = os.getenv("GARMINTOKENS", ".garmin_tokens")
    return Settings(
        garmin_email=email,
        garmin_password=password,
        garmin_tokenstore=tokenstore,
    )
