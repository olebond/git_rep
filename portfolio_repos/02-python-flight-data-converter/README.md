# Python Flight Data Converter

Small Python CLI project for converting flight time columns from `HHMM` format into ISO datetime values.

## What This Project Shows

- Python package structure with `src/`
- CSV reading and writing
- JSON export
- CLI with `argparse`
- Input validation and error handling
- Unit tests with `pytest`

## Project Structure

```text
src/flight_data_converter/
  converter.py
  cli.py
tests/
  test_converter.py
data/
  sample_flights.csv
```

## Run Locally

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
pytest
flight-convert data/sample_flights.csv output.json --format json
```

## Interview Summary

This project demonstrates clean Python fundamentals for data processing: reading raw files, validating input, transforming data, exporting results, and testing core logic.
