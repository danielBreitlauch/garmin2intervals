# garmin2intervals

Syncs Garmin Connect activities to [intervals.icu](https://intervals.icu), for
a Garmin **child/family account** that can't use intervals.icu's own native
Garmin sync.

## Why this exists

intervals.icu's built-in Garmin integration goes through Garmin's official
partner OAuth/SSO flow. Garmin child/family accounts can't complete that flow
(confirmed: the `garminconnect` library's widget/SSO login strategy is
explicitly rejected for these accounts with "Unable To Sign In"), so that
native sync path doesn't work for a child's account.

They *can* still log in with their own email/password through Garmin's other
login surfaces (the ones behind the mobile app rather than the web SSO
widget) - confirmed working end-to-end against a real child account via
`garmin2intervals-smoke-test`, both a fresh login and a cached-token login.
So this project logs in directly as the child account; no parent-account
involvement is needed.

## Status

- [x] Project scaffold (devenv/uv/pyproject)
- [x] Garmin Connect login (token-cached, MFA-aware) and activity fetching -
      see `garmin2intervals/client.py` - verified against a real child account
- [x] Download activities as FIT files, renamed by date/location/duration -
      see `garmin2intervals/naming.py`
- [x] intervals.icu activity fetch + dedup against Garmin's activity list by
      local start time and moving duration, so re-running only downloads
      what's actually new - see `garmin2intervals/intervals.py` / `sync.py`
- [x] Dockerfile + docker-compose.yml to run the sync as a polling loop -
      see "Running with Docker" below
- [x] intervals.icu upload - `IntervalsClient.upload_activity()`, wired into
      `garmin2intervals-download-activities` - verified end-to-end against
      the real accounts: a genuinely new Garmin activity was downloaded,
      uploaded, confirmed present on intervals.icu with the right name/type,
      and a second run correctly saw it as already synced (no re-upload)

## Setup

```
cp .env.example .env   # fill in GARMIN_EMAIL / GARMIN_PASSWORD / INTERVALS_API_KEY
devenv shell           # or: uv sync
uv run pytest
```

## Manual smoke tests

`tests/` is fully mocked - nothing there touches the real Garmin/intervals.icu
APIs. To verify against your actual accounts:

```
# Garmin login only (completes MFA once if needed, cached in GARMINTOKENS after)
uv run garmin2intervals-smoke-test

# Downloads Garmin activities not already on intervals.icu into ./activities/,
# then uploads each one to intervals.icu
uv run garmin2intervals-download-activities
```

## Running with Docker

Garmin has no push/webhook or long-poll API available to this unofficial
client (the official Health API does, but that requires the same partner
OAuth relationship that's blocked for a child account - see "Why this
exists"), so the container just polls `garmin2intervals-download-activities`
on an interval (`SYNC_INTERVAL_SECONDS`, default 1800s) - see `entrypoint.sh`.

Complete the first (possibly MFA) login on the host first, via the manual
smoke test above - that's what creates `.garmin_tokens/`, which is
bind-mounted into the container so it doesn't need to repeat that login:

```
cp .env.example .env   # fill in credentials, plus HOST_UID/HOST_GID (`id -u`/`id -g`)
uv run garmin2intervals-smoke-test   # first login, completes MFA if needed
docker compose up -d
docker compose logs -f
```

Downloaded activities land in `./activities/` on the host either way (both
`GARMINTOKENS` and `ACTIVITIES_DIR` are bind-mounted, not container-internal
state).
