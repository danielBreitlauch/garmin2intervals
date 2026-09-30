"""intervals.icu API client.

Only fetching is implemented so far (used by sync.py to dedup against
Garmin's activity list) - uploading is future work, see README's Status
section.

Auth is HTTP Basic with the literal username "API_KEY" and the actual key as
the password - that's intervals.icu's documented scheme, not a placeholder.
"""

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
