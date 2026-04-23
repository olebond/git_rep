# Airflow File Pipeline

Small Apache Airflow project that demonstrates a simple file ingestion workflow.

## What This Project Shows

- Airflow DAG structure
- BashOperator usage
- Docker Compose-based local Airflow environment
- Basic orchestration workflow from input to bronze folder

## Project Structure

```text
dags/
  file_copy_dag.py
docker-compose.yaml
data/
  input/
docs/
```

## Suggested Improvements

- Add a sample input file
- Add a validation task after copy
- Add a task that writes metadata about the loaded file
- Add a small architecture diagram to the README

## Interview Summary

This project demonstrates orchestration basics and can be extended into a file-based ingestion pipeline using Airflow.
