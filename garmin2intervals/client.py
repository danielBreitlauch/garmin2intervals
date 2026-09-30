"""Garmin Connect authentication and activity fetching.

Garmin child/family accounts are blocked from independent SSO login (the
`garminconnect` library detects this explicitly - see its client.py's "Widget
login: account may be a Garmin child/family account" warning). There is no
separate username/password for a child account to hand to intervals.icu's own
Garmin integration, which is why that native sync doesn't work for one.

The only way in is through the parent's own authenticated session: Garmin's
app/web UI lets the parent "switch" to viewing a child's activities from
their family view. That mechanism isn't part of any public API and isn't
implemented by `garminconnect`, so `get_family_members` / `get_activities_for`
below are the integration point for it once the real Garmin Connect API calls
behind that switch have been identified (see README's "Child account access"
section) - `connectapi` is exposed on `GarminClient` as an escape hatch for
calling that endpoint directly in the meantime.
"""

import logging
from typing import Any

from garminconnect import Garmin, GarminConnectAuthenticationError

logger = logging.getLogger(__name__)


class GarminClient:
    """Thin wrapper around `garminconnect.Garmin` with token-cached login."""

    def __init__(self, email: str, password: str, tokenstore: str) -> None:
        self._tokenstore = tokenstore
        self._garmin = Garmin(email=email, password=password)

    def login(self) -> None:
        """Log in, reusing cached tokens in `tokenstore` when possible.

        Raises `garminconnect.GarminConnectAuthenticationError` if MFA is
        required and no cached token is available - this wrapper is meant for
        non-interactive runs (scheduled sync); run the manual smoke test once
        first to complete MFA and populate the token cache.
        """
        needs_mfa, _ = self._garmin.login(self._tokenstore)
        if needs_mfa:
            raise GarminConnectAuthenticationError(
                "MFA required and no cached token found. Run the manual "
                "smoke test interactively first to complete MFA once and "
                "populate the token cache."
            )

    def get_activities(self, start: int = 0, limit: int = 20) -> list[dict[str, Any]]:
        """Return the parent account's own recent activities."""
        activities = self._garmin.get_activities(start=start, limit=limit)
        return activities if isinstance(activities, list) else []

    def connectapi(self, path: str, params: dict[str, Any] | None = None) -> Any:
        """Call an arbitrary Garmin Connect API endpoint.

        Escape hatch for the child/family activity endpoint until it's
        identified and wrapped in a dedicated method - see module docstring.
        """
        return self._garmin.connectapi(path, params=params)
