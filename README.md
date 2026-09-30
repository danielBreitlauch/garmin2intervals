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
      local start time, so re-running only downloads what's actually new -
      see `garmin2intervals/intervals.py` / `sync.py` - verified against the
      real account (13 pre-existing September activities correctly excluded)
- [ ] intervals.icu upload client (only fetching is implemented so far)
- [ ] Scheduling

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

# Downloads Garmin activities not already on intervals.icu into ./activities/
uv run garmin2intervals-download-activities
```
