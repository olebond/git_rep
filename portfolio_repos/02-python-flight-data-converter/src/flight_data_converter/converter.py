from __future__ import annotations

import csv
import json
from datetime import datetime, timedelta
from pathlib import Path

TIME_COLUMNS = (
    "SCHEDULED_DEPARTURE",
    "DEPARTURE_TIME",
    "WHEELS_OFF",
    "WHEELS_ON",
    "SCHEDULED_ARRIVAL",
    "ARRIVAL_TIME",
)


def convert_hhmm_to_iso(year: str, month: str, day: str, value: str) -> str:
    """Convert HHMM flight time into ISO datetime format."""
    if value is None or value == "":
        return ""

    if not value.isdigit() or len(value) != 4:
        raise ValueError(f"Expected HHMM value, got: {value}")

    hours = int(value[:2])
    minutes = int(value[2:])

    if hours > 24 or minutes > 59:
        raise ValueError(f"Invalid HHMM value: {value}")

    base_date = datetime(int(year), int(month), int(day))
    return (base_date + timedelta(hours=hours, minutes=minutes)).isoformat()


def process_flights(input_path: str | Path) -> tuple[list[str], list[list[str]]]:
    input_path = Path(input_path)
    if input_path.suffix.lower() != ".csv":
        raise ValueError("Input file must be a CSV file")
    if not input_path.exists():
        raise FileNotFoundError(f"Input file not found: {input_path}")

    with input_path.open(newline="", encoding="utf-8") as file:
        reader = csv.reader(file)
        header = next(reader)
        output_header = header[3:]

        missing_columns = [column for column in TIME_COLUMNS if column not in output_header]
        if missing_columns:
            raise ValueError(f"Missing required time columns: {', '.join(missing_columns)}")

        time_indexes = [output_header.index(column) for column in TIME_COLUMNS]
        output_rows: list[list[str]] = []

        for row in reader:
            year, month, day = row[:3]
            output_row = row[3:]

            for index in time_indexes:
                output_row[index] = convert_hhmm_to_iso(year, month, day, output_row[index])

            output_rows.append(output_row)

    return output_header, output_rows


def write_csv(output_path: str | Path, header: list[str], rows: list[list[str]]) -> None:
    with Path(output_path).open("w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(header)
        writer.writerows(rows)


def write_json(output_path: str | Path, header: list[str], rows: list[list[str]]) -> None:
    records = [dict(zip(header, row)) for row in rows]
    with Path(output_path).open("w", encoding="utf-8") as file:
        json.dump(records, file, indent=2)
