import io
import logging
import zipfile
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

    def download_activity_fit(self, activity_id: int | str) -> bytes:
        """Download an activity's original FIT file.

        Garmin's "original" download is a zip containing a single FIT file
        (or, rarely, a folder of them for multi-sport activities) - unzip and
        return the first file's bytes.
        """
        zip_bytes = self._garmin.download_activity(
            str(activity_id), dl_fmt=Garmin.ActivityDownloadFormat.ORIGINAL
        )
        with zipfile.ZipFile(io.BytesIO(zip_bytes)) as archive:
            name = archive.namelist()[0]
            return archive.read(name)
