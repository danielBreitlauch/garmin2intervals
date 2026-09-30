from datetime import datetime

from garmin2intervals.sync import ActivitySignature, existing_signatures, find_new_activities


def test_existing_signatures_parses_start_time_and_moving_duration():
    intervals_activities = [
        {"id": "i1", "start_date_local": "2026-09-27T15:57:20", "moving_time": 7937},
        {"id": "i2", "start_date_local": "2026-09-22T18:33:23", "moving_time": 1343},
    ]

    result = existing_signatures(intervals_activities)

    assert result == [
        ActivitySignature(datetime(2026, 9, 27, 15, 57, 20), 7937),
        ActivitySignature(datetime(2026, 9, 22, 18, 33, 23), 1343),
    ]


def test_existing_signatures_falls_back_to_elapsed_time():
    intervals_activities = [
        {"id": "i1", "start_date_local": "2026-09-27T15:57:20", "elapsed_time": 9039}
    ]

    result = existing_signatures(intervals_activities)

    assert result == [ActivitySignature(datetime(2026, 9, 27, 15, 57, 20), 9039)]


def test_find_new_activities_filters_out_matching_start_time_and_duration():
    existing = [ActivitySignature(datetime(2026, 9, 27, 15, 57, 20), 7937)]
    garmin_activities = [
        {
            "activityId": 1,
            "startTimeLocal": "2026-09-27 15:57:20",
            "movingDuration": 7940,
        },
        {
            "activityId": 2,
            "startTimeLocal": "2026-09-28 09:00:00",
            "movingDuration": 1000,
        },
    ]

    result = find_new_activities(garmin_activities, existing)

    assert result == [garmin_activities[1]]


def test_find_new_activities_keeps_same_start_time_but_different_duration():
    """Same start second but a very different length isn't the same activity -
    same start time alone isn't enough to call it a duplicate."""
    existing = [ActivitySignature(datetime(2026, 9, 27, 15, 57, 20), 7937)]
    garmin_activities = [
        {
            "activityId": 1,
            "startTimeLocal": "2026-09-27 15:57:20",
            "movingDuration": 200,
        }
    ]

    result = find_new_activities(garmin_activities, existing)

    assert result == garmin_activities


def test_find_new_activities_keeps_activities_with_unreadable_start_time():
    garmin_activities = [{"activityId": 3, "startTimeLocal": None}]

    result = find_new_activities(garmin_activities, existing=[])

    assert result == garmin_activities


def test_find_new_activities_allows_small_duration_drift():
    existing = [ActivitySignature(datetime(2026, 9, 27, 15, 57, 20), 7937)]
    garmin_activities = [
        {
            "activityId": 1,
            "startTimeLocal": "2026-09-27 15:57:20",
            "movingDuration": 7970,  # 33s off - well within tolerance
        }
    ]

    result = find_new_activities(garmin_activities, existing)

    assert result == []
