# garmin2intervals

Syncs Garmin Connect activities to [intervals.icu](https://intervals.icu), for
a Garmin **child/family account** that can't use intervals.icu's own native
Garmin sync.

## Why this exists

intervals.icu's built-in Garmin integration expects to log in with the
account's own Garmin Connect username and password. Garmin child/family
accounts are blocked from that kind of independent SSO login entirely (the
`garminconnect` library detects and reports this explicitly), so that native
sync path doesn't work for a child's account.

The only way to reach the child's activities is through the **parent's own**
authenticated Garmin session - Garmin's app/web UI lets the parent switch to
viewing a child's data from their family view. This project drives that.

## Status

- [x] Project scaffold (devenv/uv/pyproject)
- [x] Parent-account Garmin Connect login (token-cached, MFA-aware) and
      activity fetching - see `garmin2intervals/client.py`
- [ ] **Child account access** - the API call(s) behind Garmin's "switch to
      child" UI aren't documented anywhere (not in the `garminconnect`
      library, not in any other open-source Garmin Connect client, not in
      Garmin's own docs). These need to be captured directly from a real
      family account's network traffic before they can be implemented
      reliably. `GarminClient.connectapi()` is the escape hatch for calling
      whatever endpoint that turns out to be.
- [ ] intervals.icu upload client
- [ ] Sync orchestration (dedup, scheduling)

## Setup

```
cp .env.example .env   # fill in GARMIN_EMAIL / GARMIN_PASSWORD (parent account)
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
