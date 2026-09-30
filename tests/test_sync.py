from datetime import datetime

from garmin2intervals.sync import existing_start_times, find_new_activities


def test_existing_start_times_parses_local_start_dates():
    intervals_activities = [
        {"id": "i1", "start_date_local": "2026-09-27T15:57:20"},
        {"id": "i2", "start_date_local": "2026-09-22T18:33:23"},
    ]

    result = existing_start_times(intervals_activities)

    assert result == {
        datetime(2026, 9, 27, 15, 57, 20),
        datetime(2026, 9, 22, 18, 33, 23),
    }


def test_find_new_activities_filters_out_matching_start_times():
    existing = {datetime(2026, 9, 27, 15, 57, 20)}
    garmin_activities = [
        {"activityId": 1, "startTimeLocal": "2026-09-27 15:57:20"},
        {"activityId": 2, "startTimeLocal": "2026-09-28 09:00:00"},
    ]

    result = find_new_activities(garmin_activities, existing)

    assert result == [{"activityId": 2, "startTimeLocal": "2026-09-28 09:00:00"}]


def test_find_new_activities_keeps_activities_with_unreadable_start_time():
    garmin_activities = [{"activityId": 3, "startTimeLocal": None}]

    result = find_new_activities(garmin_activities, existing=set())

    assert result == garmin_activities
