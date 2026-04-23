# Spark Batch Data Quality

PySpark mini-project for validating transaction datasets with schema and data quality checks.

## What This Project Shows

- Local Spark session setup
- CSV loading with inferred schema
- Column count validation
- Data type validation
- Payment format checks
- Basic automated tests around Spark helper functions

## Project Structure

```text
src/
  data_quality.py
tests/
  test_data_quality.py
data/
  transactions_valid.csv
  transactions_invalid.csv
```

## Run Locally

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
PYTHONPATH=src pytest
```

## Interview Summary

This project demonstrates practical PySpark basics and data quality thinking: loading structured data, checking schema assumptions, and testing reusable validation functions.
