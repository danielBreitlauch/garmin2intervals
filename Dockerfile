# syntax=docker/dockerfile:1

# uv's own distroless image is just used as a source of the `uv` binary below.
FROM ghcr.io/astral-sh/uv:latest AS uv

FROM python:3.13-slim-bookworm AS builder

COPY --from=uv /uv /usr/local/bin/uv

WORKDIR /app

ENV UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    UV_PYTHON_DOWNLOADS=never

# Dependencies first, in their own layer keyed only on the lockfile, so an edit to
# garmin2intervals/ doesn't invalidate the dependency install step on every rebuild.
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-install-project --no-dev

COPY README.md ./
COPY garmin2intervals ./garmin2intervals
RUN uv sync --frozen --no-dev


FROM python:3.13-slim-bookworm AS runtime

WORKDIR /app

RUN groupadd --system app && useradd --system --gid app --home-dir /app app

COPY --from=builder /app/.venv ./.venv
COPY --from=builder /app/garmin2intervals ./garmin2intervals

# No `uv` binary needed at runtime - the venv's own console-script entry points
# (garmin2intervals-*) are put on PATH and run directly.
ENV PATH="/app/.venv/bin:$PATH" \
    PYTHONUNBUFFERED=1

# activities/ and .garmin_tokens/ are the only state this app writes - see
# docker-compose.yml, which bind-mounts both from the host so downloaded
# activities and the cached Garmin login survive a container restart/rebuild.
RUN mkdir -p activities .garmin_tokens \
    && chown -R app:app /app

VOLUME ["/app/activities", "/app/.garmin_tokens"]

USER app

ENTRYPOINT ["garmin2intervals-download-activities"]
