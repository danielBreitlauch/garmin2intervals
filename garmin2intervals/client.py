"""Garmin Connect authentication and activity fetching.

Garmin child/family accounts can't complete the browser SSO/OAuth flow that
intervals.icu's own Garmin partner integration relies on (the `garminconnect`
library detects and rejects this explicitly - see its client.py's "Widget
login: account may be a Garmin child/family account" warning) - that's why
that native sync doesn't work for a child account.

They *can* still log in directly with their own email/password through the
library's other strategies (the ones behind the mobile app rather than the
web SSO widget), confirmed against a real child account. So this client just
logs in with the child's own credentials - no parent-account involvement
needed.
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
        """Return the account's recent activities."""
        activities = self._garmin.get_activities(start=start, limit=limit)
        return activities if isinstance(activities, list) else []

    def connectapi(self, path: str, params: dict[str, Any] | None = None) -> Any:
        """Call an arbitrary Garmin Connect API endpoint not otherwise wrapped."""
        return self._garmin.connectapi(path, params=params)
