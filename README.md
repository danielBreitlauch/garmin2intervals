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
- [ ] intervals.icu upload client
- [ ] Sync orchestration (dedup, scheduling)

## Setup

```
cp .env.example .env   # fill in GARMIN_EMAIL / GARMIN_PASSWORD
devenv shell           # or: uv sync
uv run pytest
```

## Manual smoke test

`tests/` is fully mocked - nothing there touches the real Garmin API. To
verify against your actual account (and complete MFA once, which then gets
cached in `GARMINTOKENS` for subsequent runs):

```
uv run garmin2intervals-smoke-test
```
