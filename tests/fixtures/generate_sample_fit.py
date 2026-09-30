"""Regenerates sample.fit: a synthetic FIT file (fabricated start time,
duration, distance and GPS - "null island", 0/0) used to exercise
naming.read_fit_summary's real fitparse parsing path without any real
activity data. Not part of the project's own dependencies (only needed to
regenerate the fixture) - run via:

    uv run --with fit-tool python3 tests/fixtures/generate_sample_fit.py
"""

import calendar
import datetime
from pathlib import Path

from fit_tool.fit_file_builder import FitFileBuilder
from fit_tool.profile.messages.activity_message import ActivityMessage
from fit_tool.profile.messages.event_message import EventMessage
from fit_tool.profile.messages.file_id_message import FileIdMessage
from fit_tool.profile.messages.session_message import SessionMessage
from fit_tool.profile.profile_type import Event, EventType, FileType, Manufacturer, Sport, SubSport

FIT_EPOCH = 631065600  # seconds between the Unix epoch and FIT's (1989-12-31)


def _ms(dt: datetime.datetime) -> int:
    return round(dt.timestamp() * 1000)


def _local_timestamp_raw(naive_local_dt: datetime.datetime) -> int:
    """`local_timestamp` fields (unlike `timestamp`) take a raw FIT-epoch
    value with no unit conversion - see ActivityLocalTimestampField
    (offset=0, scale=1) vs TimestampField (offset/scale convert from ms).
    """
    return calendar.timegm(naive_local_dt.timetuple()) - FIT_EPOCH


def main() -> None:
    start = datetime.datetime(2020, 1, 1, 10, 0, 0, tzinfo=datetime.timezone.utc)
    local_start_naive = datetime.datetime(2020, 1, 1, 11, 0, 0)  # UTC+1
    duration_s = 1800
    end = start + datetime.timedelta(seconds=duration_s)
    local_end_naive = local_start_naive + datetime.timedelta(seconds=duration_s)

    builder = FitFileBuilder(strict=False, auto_define=True)

    file_id = FileIdMessage()
    file_id.type = FileType.ACTIVITY
    file_id.manufacturer = Manufacturer.GARMIN.value
    file_id.product = 1
    file_id.serial_number = 1
    file_id.time_created = _ms(start)
    builder.add(file_id)

    start_event = EventMessage()
    start_event.timestamp = _ms(start)
    start_event.event = Event.TIMER
    start_event.event_type = EventType.START
    builder.add(start_event)

    stop_event = EventMessage()
    stop_event.timestamp = _ms(end)
    stop_event.event = Event.TIMER
    stop_event.event_type = EventType.STOP_ALL
    builder.add(stop_event)

    session = SessionMessage()
    session.timestamp = _ms(end)
    session.start_time = _ms(start)
    session.total_elapsed_time = duration_s
    session.total_timer_time = duration_s
    session.total_distance = 12345.6
    session.sport = Sport.CYCLING
    session.sub_sport = SubSport.ROAD
    session.first_lap_index = 0
    session.num_laps = 1
    session.start_position_lat = 0.0
    session.start_position_long = 0.0
    builder.add(session)

    activity = ActivityMessage()
    activity.timestamp = _ms(end)
    activity.local_timestamp = _local_timestamp_raw(local_end_naive)
    activity.num_sessions = 1
    activity.total_timer_time = duration_s
    builder.add(activity)

    out_path = Path(__file__).parent / "sample.fit"
    out_path.write_bytes(builder.build_bytes())
    print(f"wrote {out_path}")


if __name__ == "__main__":
    main()
