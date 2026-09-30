#!/bin/sh
# Garmin Connect has no push/webhook or long-poll API available to this
# unofficial client (the official Health API does, but that requires the
# same partner OAuth relationship that's blocked for a child account - see
# README) - this loop polls garmin2intervals-download-activities on an
# interval instead. Backgrounding the sleep and trapping into `wait` (rather
# than a plain foreground `sleep`) lets SIGTERM stop the container promptly
# instead of waiting out the rest of the interval.

SYNC_INTERVAL_SECONDS="${SYNC_INTERVAL_SECONDS:-1800}"

term_handler() {
    exit 0
}
trap term_handler TERM INT

while true; do
    garmin2intervals-download-activities
    echo "Sleeping ${SYNC_INTERVAL_SECONDS}s until next sync..." >&2
    sleep "$SYNC_INTERVAL_SECONDS" &
    wait $!
done
