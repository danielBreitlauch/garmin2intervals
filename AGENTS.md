# Coding Agent Guidelines for garmin2intervals

- **Simplicity first**: personal, single-maintainer project. No framework scaffolding, no config layers, no abstraction "for later".
- **Surgical changes only**: touch only what's necessary.
- **No comments by default**: write one only when the *why* isn't obvious from the code (a Garmin API quirk, a non-obvious constraint). Never restate what the code already says.

## Project

A small package, `garmin2intervals`, that authenticates against Garmin Connect (via the `garminconnect` library, using the child's own credentials directly - see `garmin2intervals/client.py`) and pushes activities to intervals.icu. This exists because intervals.icu's own native Garmin sync goes through an OAuth/SSO flow that Garmin blocks for child/family accounts, even though direct email/password login still works for them.

- **`client.py`** - Garmin Connect auth (token-cached) and activity fetching.
- **`intervals.py`** - intervals.icu API client for uploading/creating activities.
- **`sync.py`** - orchestrates client -> intervals.

## Tech Stack

- **Language:** Python 3.13
- **Package/dependency management:** `uv`; build backend `hatchling`
- **Dev environment:** `devenv` (Nix) - `devenv.nix` runs `uv sync` on shell entry; `.envrc`/`direnv` activates it
- **Garmin API:** unofficial `garminconnect` package (reverse-engineered, no public Garmin Connect Developer Program access for this use case)

## Testing

`uv run pytest`. Garmin/intervals.icu calls are mocked in tests - no test should hit the real APIs. A manual, credentials-required smoke script lives outside the test suite (see README) for verifying against the real accounts.

## What to run after a change

`uv run pytest` and, if `client.py`/`intervals.py` changed, a manual run against real credentials before trusting the change (see README).
