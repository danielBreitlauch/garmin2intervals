from typing import Any

import requests

BASE_URL = "https://intervals.icu/api/v1"


class IntervalsClient:
    def __init__(self, api_key: str, athlete_id: str = "0") -> None:
        self._auth = ("API_KEY", api_key)
        self._athlete_id = athlete_id

    def get_activities(self, oldest: str, newest: str) -> list[dict[str, Any]]:
        """Activities with local start date in [oldest, newest] (YYYY-MM-DD)."""
        resp = requests.get(
            f"{BASE_URL}/athlete/{self._athlete_id}/activities",
            params={"oldest": oldest, "newest": newest},
            auth=self._auth,
            timeout=30,
        )
        resp.raise_for_status()
        return resp.json()

    def upload_activity(
        self,
        fit_bytes: bytes,
        filename: str,
        external_id: str | None = None,
        name: str | None = None,
    ) -> dict[str, Any]:
        """Upload a FIT file as a new activity.

        Returns the parsed JSON response (has an "id"); intervals.icu answers
        201 if it created a new activity, 200 if the upload matched/merged
        into one that already existed - both are treated as success here.
        """
        params = {k: v for k, v in {"external_id": external_id, "name": name}.items() if v}
        resp = requests.post(
            f"{BASE_URL}/athlete/{self._athlete_id}/activities",
            params=params,
            files={"file": (filename, fit_bytes, "application/octet-stream")},
            auth=self._auth,
            timeout=60,
        )
        resp.raise_for_status()
        return resp.json()
