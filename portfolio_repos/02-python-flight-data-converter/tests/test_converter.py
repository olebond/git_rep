from pathlib import Path

import pytest

from flight_data_converter import convert_hhmm_to_iso, process_flights


FIXTURE = Path(__file__).parent.parent / "data" / "sample_flights.csv"


def test_convert_regular_time_to_iso_datetime():
    assert convert_hhmm_to_iso("2015", "7", "1", "0830") == "2015-07-01T08:30:00"


def test_convert_2400_to_next_day_midnight():
    assert convert_hhmm_to_iso("2015", "7", "1", "2400") == "2015-07-02T00:00:00"


def test_process_flights_converts_time_columns():
    header, rows = process_flights(FIXTURE)

    assert "SCHEDULED_DEPARTURE" in header
    assert rows[0][header.index("SCHEDULED_DEPARTURE")] == "2015-07-02T00:00:00"
    assert rows[1][header.index("ARRIVAL_TIME")] == "2015-07-01T05:52:00"


def test_invalid_time_raises_value_error():
    with pytest.raises(ValueError):
        convert_hhmm_to_iso("2015", "7", "1", "2465")
